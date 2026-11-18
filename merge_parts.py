#!/usr/bin/env python3
"""合并工具级注释分片 + server 级注释 -> supply-annotations/mcp/<entry>.json。

分片形状：_parts/<entry>.<NN>.json  =  {"tools": {<leaf>: {...}}}
server 级：server-annotations.json   =  {"entries": {<entry>: {human, canonical}}}

合并规则：
  - 同一条目的分片按文件名排序合并；同一 leaf 出现在两个分片 -> 报错（不静默覆盖）
  - 缺 server 级注释的条目 -> 报错（server 级必须有）
  - 输出按 tools 键排序、固定缩进，保证同输入同输出

用法：
    python3 supply-annotations/merge_parts.py            # 全部
    python3 supply-annotations/merge_parts.py --only fd-daas-mcp
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "_parts"
MCP = ROOT / "mcp"
SERVER = ROOT / "server-annotations.json"
PROVENANCE = {"source": "finddata-supply-annotations", "updatedAt": "2026-11-02"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只合并某条目")
    args = ap.parse_args()

    server_doc = json.loads(SERVER.read_text(encoding="utf-8"))
    servers = server_doc["entries"]

    by_entry: dict[str, list[Path]] = {}
    for p in sorted(PARTS.glob("*.json")):
        if p.name.startswith("_"):  # _plan.json 等元数据文件不是分片
            continue
        entry = p.name.split(".")[0]
        by_entry.setdefault(entry, []).append(p)
    if args.only:
        by_entry = {k: v for k, v in by_entry.items() if k == args.only}

    errors: list[str] = []
    written = 0
    for entry, files in sorted(by_entry.items()):
        if entry not in servers:
            errors.append(f"{entry}: 缺 server 级注释（server-annotations.json）")
            continue
        tools: dict[str, dict] = {}
        for p in files:
            doc = json.loads(p.read_text(encoding="utf-8"))
            part = doc.get("tools") or {}
            dup = set(part) & set(tools)
            if dup:
                errors.append(f"{entry}: 分片重复声明工具 {sorted(dup)[:5]}")
            tools.update(part)
        ann = {
            "human": servers[entry]["human"],
            "canonical": servers[entry].get("canonical", {}),
            "tools": {k: tools[k] for k in sorted(tools)},
            "provenance": PROVENANCE,
        }
        out = {"version": 1, "server": entry, "annotation": ann}
        text = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
        (MCP / f"{entry}.json").write_text(text, encoding="utf-8")
        written += 1
        print(f"  {entry:32} tools={len(tools):>4}  parts={len(files)}")

    missing = sorted(set(by_entry) - set(servers))
    if missing:
        errors.append(f"缺 server 级注释: {', '.join(missing)}")

    print(f"\n写入 {written} 个条目 -> {MCP}")
    if errors:
        print(f"失败 {len(errors)} 项：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
