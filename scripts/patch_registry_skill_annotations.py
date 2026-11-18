#!/usr/bin/env python3
"""registry 技能卡注释直补（add-skill-supply-annotations 4.1，幂等 upsert）。

读 dist/market-annotations.json 的 skills 键（origin=registry 两域中的 registry 域），
对 registry 活栈 agent_skills_default 的每张技能卡写 metadata.extra.annotations
（registry API PUT 把自定义键收进 metadata.extra——这是 API 编辑后仍存活的落点；
bridge/读面以该路径为 skill 注释消费位）。

- 幂等：同内容重跑零写入（比对后 skip）。
- 合并：只动 extra.annotations，卡上其它 extra 键原样保留。
- 漂移：卡不存在（新上架未注释）→ 点名并以非零退出；本地缺卡（registry 新增）→
  先重取快照（scripts/enumerate_registry_skills.py）再跑覆盖门。

用法：
    python3 scripts/patch_registry_skill_annotations.py [--dry-run] [--only <name>]
前置：kubectl 可达 cheap 集群 mcp-registry（context cheap）。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "market-annotations.json"
CTX = "cheap"
NS = "mcp-registry"
NS = "mcp-registry"  # noqa: E305 (kept for clarity)


def registry_pod() -> str:
    rows = kubectl_read(["get", "pods", "-o", "name"]).splitlines()
    pod = next((l.strip() for l in rows if "pod/registry-" in l and "auth" not in l), None)
    if not pod:
        raise RuntimeError("registry pod not found")
    return pod


POD_TMP = "/tmp/skill-annotations-payload.json"


def kubectl_read(args: list[str]) -> str:
    out = subprocess.run(["kubectl", "--context", CTX, "-n", NS, *args],
                         capture_output=True, text=True, timeout=120, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"kubectl {' '.join(args[:3])} failed: {out.stderr[:400]}")
    return out.stdout


def kubectl(args: list[str], input_text: str | None = None) -> str:
    out = subprocess.run(["kubectl", "--context", CTX, "-n", NS, *args],
                         capture_output=True, text=True, timeout=120,
                         input=input_text, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"kubectl {' '.join(args[:3])} failed: {out.stderr[:400]}")
    return out.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只报告将写入什么，不落库")
    ap.add_argument("--only", help="只补一个技能（默认全量）")
    args = ap.parse_args()

    if not DIST.exists():
        print("缺 dist/market-annotations.json —— 先跑 export.py", file=sys.stderr)
        return 2
    skills = json.loads(DIST.read_text(encoding="utf-8")).get("skills") or {}
    registry_domain = {n: v for n, v in skills.items() if v.get("origin") == "registry"}
    if args.only:
        registry_domain = {n: v for n, v in registry_domain.items() if n == args.only}
        if not registry_domain:
            print(f"--only {args.only}: 产物中没有该技能", file=sys.stderr)
            return 2
    print(f"载荷：{len(registry_domain)} 张技能卡注释（origin=registry）")

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(registry_domain, f, ensure_ascii=False)
        payload_path = f.name

    pod = registry_pod().removeprefix("pod/")
    kubectl(["cp", payload_path, f"{pod}:{POD_TMP}"])

    script = r'''
import os, json
from pymongo import MongoClient
u=os.environ["DOCUMENTDB_USERNAME"]; p=os.environ["DOCUMENTDB_PASSWORD"]
h=os.environ["DOCUMENTDB_HOST"]; port=os.environ.get("DOCUMENTDB_PORT","27017"); dbn=os.environ["DOCUMENTDB_DATABASE"]
c=MongoClient(f"mongodb://{u}:{p}@{h}:{port}/{dbn}?authSource=admin", serverSelectionTimeoutMS=4000)
col=c[dbn]["agent_skills_default"]
payload=json.load(open("''' + POD_TMP + r'''"))
dry = os.environ.get("DRY_RUN") == "1"
patched=unchanged=missing=0
missing_names=[]
for name, val in sorted(payload.items()):
    card = col.find_one({"_id": f"/skills/{name}"}, {"metadata.extra": 1})
    if not card:
        missing += 1; missing_names.append(name); continue
    extra = (card.get("metadata") or {}).get("extra") or {}
    current = extra.get("annotations")
    desired = {"human": val["annotation"]["human"], "provenance": val["annotation"].get("provenance")}
    if json.dumps(current, sort_keys=True, ensure_ascii=False) == json.dumps(desired, sort_keys=True, ensure_ascii=False):
        unchanged += 1; continue
    if not dry:
        extra = dict(extra); extra["annotations"] = desired
        col.update_one({"_id": f"/skills/{name}"}, {"$" + "set": {"metadata.extra": extra}})
    patched += 1
print(json.dumps({"patched": patched, "unchanged": unchanged, "missing": missing,
                  "missing_names": missing_names[:10]}, ensure_ascii=False))
'''
    env = "DRY_RUN=1 " if args.dry_run else ""
    out = kubectl(["exec", pod, "--", "sh", "-c",
                   f'{env}/app/.venv/bin/python3 - <<\'PYEOF\'\n{script}\nPYEOF'])
    report = json.loads(out.strip().splitlines()[-1])
    print(f"结果：写入 {report['patched']} / 已一致 {report['unchanged']} / 卡缺失 {report['missing']}")
    if report["missing"]:
        print("缺失卡（registry 新上架未注释）:", ", ".join(report["missing_names"]), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
