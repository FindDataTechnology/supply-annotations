#!/usr/bin/env python3
"""把 supply-annotations/{mcp,skills}/*.json 汇总为 paas 消费的 market-annotations.json。

产物形状（对齐 docs/mcp-annotation-source-requirements.md + add-skill-supply-annotations）：

    {
      "version": 1,
      "entries": { "<registry name>": { "annotation": {...} } },   # 仅 MCP 条目
      "skills":  { "<skill name>": { "origin": "registry|yizuo-file",
                                     "annotation": {...} } }       # 两域技能
    }

稳定性：条目按 name 排序、ensure_ascii=False、固定缩进——同输入同输出逐字节一致。
任何条目缺 zh 主轨 / 缺五语 / （MCP）工具覆盖不足时，**不导出该条目**并以非零退出并点名。
skill 名与 server 名跨键集合 MUST NOT 相交（相交 = paas 侧键空间腐化），相交即整体失败。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MCP_DIR = ROOT / "mcp"
SKILLS_DIR = ROOT / "skills"
SRC_DIR = ROOT / "_sources"
OUT = ROOT / "dist" / "market-annotations.json"
LOCALES = ["zh", "en", "ja", "es", "fr"]
SKILL_ORIGINS = ("registry", "yizuo-file")


def entry_problems(name: str, doc: dict) -> list[str]:
    problems: list[str] = []
    ann = doc.get("annotation") or {}
    human = ann.get("human") or {}
    if doc.get("server") != name:
        problems.append(f"{name}: server 字段与文件名不一致")
    if not isinstance(human.get("zh"), dict):
        problems.append(f"{name}: 缺 zh 主轨")
    for loc in LOCALES:
        if loc not in human:
            problems.append(f"{name}: 缺 {loc} 轨")
    src = SRC_DIR / f"{name}.tools.json"
    if src.exists():
        upstream = {t["name"] for t in json.loads(src.read_text(encoding="utf-8")).get("tools", [])}
        got = set((ann.get("tools") or {}).keys())
        missing = upstream - got
        extra = got - upstream
        if missing:
            problems.append(f"{name}: 覆盖缺 {len(missing)} 个工具（如 {sorted(missing)[0]}）")
        if extra:
            problems.append(f"{name}: 注释多 {len(extra)} 个工具（如 {sorted(extra)[0]}）")
    return problems


def skill_problems(name: str, doc: dict) -> list[str]:
    problems: list[str] = []
    ann = doc.get("annotation") or {}
    human = ann.get("human") or {}
    if doc.get("skill") != name:
        problems.append(f"{name}: skill 字段与文件名不一致")
    if doc.get("origin") not in SKILL_ORIGINS:
        problems.append(f"{name}: origin 缺失或非法")
    if not isinstance(human.get("zh"), dict):
        problems.append(f"{name}: 缺 zh 主轨")
    for loc in LOCALES:
        if loc not in human:
            problems.append(f"{name}: 缺 {loc} 轨")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    mcp_files = sorted(MCP_DIR.glob("*.json"))
    if not mcp_files:
        print("没有可导出的 MCP 注释文件", file=sys.stderr)
        return 2

    entries: dict[str, dict] = {}
    skills: dict[str, dict] = {}
    rejected: list[str] = []
    for p in mcp_files:
        name = p.stem
        doc = json.loads(p.read_text(encoding="utf-8"))
        problems = entry_problems(name, doc)
        if problems:
            rejected.extend(problems)
            continue
        entries[name] = {"annotation": doc["annotation"]}

    if SKILLS_DIR.exists():
        for p in sorted(SKILLS_DIR.glob("*.json")):
            name = p.stem
            doc = json.loads(p.read_text(encoding="utf-8"))
            problems = skill_problems(name, doc)
            if problems:
                rejected.extend(problems)
                continue
            skills[name] = {"origin": doc["origin"], "annotation": doc["annotation"]}

    # 跨键空间卫兵：skill 名与 server 名必须不相交（skill 注释混进 server 键空间
    # 会被 paas 仓库注释源按 server 名合并——撞名即腐化，导出 outright 拒绝）。
    collisions = sorted(set(skills) & set(entries))
    if collisions:
        print(f"skill 名与 server 名撞键 {len(collisions)} 个，拒绝导出: {', '.join(collisions[:8])}", file=sys.stderr)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict = {"version": 1, "entries": entries}
    if skills:
        payload["skills"] = skills
    text = json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    out_path.write_text(text, encoding="utf-8")

    print(f"导出 MCP {len(entries)} 条 / 技能 {len(skills)} 条 -> {out_path}（{len(text.encode())} bytes）")
    if rejected:
        print(f"拒绝 {len(rejected)} 项：", file=sys.stderr)
        for r in rejected:
            print(f"  - {r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
