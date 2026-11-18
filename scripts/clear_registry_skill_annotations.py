#!/usr/bin/env python3
"""registry 技能卡 extra.annotations 清除（add-skill-supply-annotations 4.4 后手）。

R1=方案 B 终态（docs/skill-annotation-contract-reconciliation.md §七，paas 侧已撤
0.1 extra fallback 改走仓库 skills 键合并）：DB 直补通道退役，历史灌入的
272 行 metadata.extra.annotations 成零消费者死数据，择机清除。

- 外科手术：只 $unset metadata.extra.annotations，卡上其它 extra 键原样保留。
- 可逆：数据真源在 supply-annotations/，随时可由
  scripts/patch_registry_skill_annotations.py 幂等重灌。
- 默认 dry-run：只报告带该键的卡数与形状对账（本脚本灌入的行应带
  human+provenance 形状；异形行点名不删）。

用法：
    python3 scripts/clear_registry_skill_annotations.py            # dry-run
    python3 scripts/clear_registry_skill_annotations.py --apply    # 实际清除
前置：kubectl 可达 cheap 集群 mcp-registry（context cheap）。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

CTX = "cheap"
NS = "mcp-registry"


def kubectl(args: list[str], input_text: str | None = None) -> str:
    out = subprocess.run(["kubectl", "--context", CTX, "-n", NS, *args],
                         capture_output=True, text=True, timeout=120,
                         input=input_text, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"kubectl {' '.join(args[:3])} failed: {out.stderr[:400]}")
    return out.stdout


def registry_pod() -> str:
    rows = kubectl(["get", "pods", "-o", "name"]).splitlines()
    pod = next((l.strip() for l in rows if "pod/registry-" in l and "auth" not in l), None)
    if not pod:
        raise RuntimeError("registry pod not found")
    return pod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="实际清除（默认 dry-run）")
    args = ap.parse_args()

    pod = registry_pod().removeprefix("pod/")
    script = r'''
import os, json
from pymongo import MongoClient
u=os.environ["DOCUMENTDB_USERNAME"]; p=os.environ["DOCUMENTDB_PASSWORD"]
h=os.environ["DOCUMENTDB_HOST"]; port=os.environ.get("DOCUMENTDB_PORT","27017"); dbn=os.environ["DOCUMENTDB_DATABASE"]
c=MongoClient(f"mongodb://{u}:{p}@{h}:{port}/{dbn}?authSource=admin", serverSelectionTimeoutMS=4000)
col=c[dbn]["agent_skills_default"]
apply = os.environ.get("APPLY") == "1"
carrying = list(col.find({"metadata.extra.annotations": {"$exists": True}},
                         {"_id": 1, "metadata.extra.annotations": 1}))
ours = others = 0
other_ids = []
for card in carrying:
    ann = (card.get("metadata") or {}).get("extra", {}).get("annotations")
    if isinstance(ann, dict) and isinstance(ann.get("human"), dict) and "provenance" in ann:
        ours += 1
    else:
        others += 1
        other_ids.append(card["_id"])
removed = 0
if apply:
    res = col.update_many({"metadata.extra.annotations": {"$exists": True},
                           "metadata.extra.annotations.human": {"$type": "object"},
                           "metadata.extra.annotations.provenance": {"$exists": True}},
                          {"$" + "unset": {"metadata.extra.annotations": ""}})
    removed = res.modified_count
print(json.dumps({"carrying": len(carrying), "our_shape": ours, "other_shape": others,
                  "other_ids": other_ids[:10], "removed": removed}, ensure_ascii=False))
'''
    env = "APPLY=1 " if args.apply else ""
    out = kubectl(["exec", pod, "--", "sh", "-c",
                   f'{env}/app/.venv/bin/python3 - <<\'PYEOF\'\n{script}\nPYEOF'])
    report = json.loads(out.strip().splitlines()[-1])
    mode = "清除" if args.apply else "dry-run（加 --apply 实际清除）"
    print(f"结果[{mode}]：带键 {report['carrying']}（本脚本形状 {report['our_shape']} / 异形 {report['other_shape']}）"
          f" / 已移除 {report['removed']}")
    if report["other_shape"]:
        print("异形行（非本通道灌入，未触碰）:", ", ".join(report["other_ids"]), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
