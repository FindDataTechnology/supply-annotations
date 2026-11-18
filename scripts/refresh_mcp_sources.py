"""把 supply-annotations/_sources/<entry>.tools.json 刷成**现网**工具面（只读→写快照）。

为什么需要它：`_sources/*.tools.json` 是「产出时的上游快照」，仓里没有刷新工具，
于是它跟注释一起冻结在产出那天。上游加了工具之后，快照里没有、注释里也没有，
覆盖门就永远红——而 red 的根因其实只是快照陈旧（validate.py 自己也在注释里点过
「上游缺工具」的红可能是旧快照的红）。刷新快照是补注释的**前置**，不是补丁。

取数口径：直连各服务 **mesh NodePort** 的 MCP `tools/list`（不猜、不走公网网关），
字段只取 name + description（与既有快照同形）。写盘按 name 排序、固定缩进，
同输入同输出。

用法：
    python3 supply-annotations/scripts/refresh_mcp_sources.py --only fd-quant
    python3 supply-annotations/scripts/refresh_mcp_sources.py            # 全部可探条目
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "_sources"

#: entry -> (mesh 端点, 展示名, 一句话)。端点与 MCP-REGISTRY.md §1.1 同一真源；
#: 只收「工具面可裸探」的条目（需凭据的条目换别的取数路，见 _AUTH_GATED）。
ENDPOINTS = {
    "fd-quant": ("http://cheap5.mesh.finddata.cn:31888/mcp", "fd-quant", "确定性计算面 + 决策账本"),
    # 公网面在 chengsi 那台 docker（只滚 cheap 不生效）；两处工具面同数，探内网 cheap 即代表。
    "fd-open-data-mcp": ("http://cheap6.mesh.finddata.cn:31851/mcp", "fd-open-data-mcp",
                         "开放数据面（政策/宏观/行业/餐饮/酒店/花卉等族）"),
    "fd-info": ("http://cheap6.mesh.finddata.cn:31905/mcp", "fd-info", "柏讯信息流索引（公告/部委/SSE互动三源）"),
    "fd-erp-ledger-mcp": ("http://cheap6.mesh.finddata.cn:31910/mcp", "fd-erp-ledger-mcp", "ERP 台账/对账/计费/信用"),
    "fd-cn-report": ("http://cheap6.mesh.finddata.cn:31852/mcp", "fd-cn-report", "A股/港股/B股年报抽取与指标"),
    "fd-health-config": ("http://<health-host>:8090/mcp", "fd-health-config", "健康/配置面"),
    "fd-paper-trading": ("http://cheap6.mesh.finddata.cn:31894/mcp/", "fd-paper-trading", "模拟交易"),
    "infra-telemetry": ("http://cheap6.mesh.finddata.cn:31908/mcp", "infra-telemetry", "基础设施遥测"),
    "fd-text-core": ("http://cheap6.mesh.finddata.cn:31887/mcp", "fd-text-core", "文本核心能力"),
    "facet-ops-mcp": ("http://cheap6.mesh.finddata.cn:31892/mcp", "facet-ops-mcp", "谦面网关操作面"),
    "wanxing-ops-mcp": ("http://cheap6.mesh.finddata.cn:31895/mcp", "wanxing-ops-mcp", "萬星舰队操作面"),
    "wire-ops-mcp": ("http://cheap6.mesh.finddata.cn:31896/mcp", "wire-ops-mcp", "柏讯客户面读写"),
    "wire-build-mcp": ("http://cheap6.mesh.finddata.cn:31907/mcp", "wire-build-mcp", "柏讯对话建造与治理"),
    "lex-ops-mcp": ("http://cheap6.mesh.finddata.cn:31897/mcp", "lex-ops-mcp", "识律线操作面"),
    "fd-legal-search-mcp": ("http://cheap6.mesh.finddata.cn:31884/mcp", "fd-legal-search-mcp", "法条/案例检索"),
    "fd-sentiment": ("http://cheap6.mesh.finddata.cn:31889/mcp", "fd-sentiment", "情绪面"),
    "fd-daas-mcp": ("http://cheap6.mesh.finddata.cn:31861/mcp", "fd-daas-mcp", "数据即服务"),
    "fd-find-data-business-mcp": ("http://cheap6.mesh.finddata.cn:31886/mcp", "fd-find-data-business-mcp", "商业数据面"),
    # 启材线（教育）目录：5 工具；装鉴权门（/mcp 与 /mcp/ 双路径均 401，2026-11-12 实测），
    # 故列在 ENDPOINTS 只为让 `--only edu-catalog` 点名「需凭据」而不是报「未知 entry」。
    "edu-catalog": ("http://cheap6.mesh.finddata.cn:31909/mcp", "edu-catalog", "启材线目录查询/订阅"),
}

#: 工具面必须带凭据的条目：裸探会 401（那是在路由的判据，不是故障）。这些条目的
#: 快照要另取（registry tool_list 或 pod 内枚举），本脚本跳过并点名。
#:
#: ⚠ 这份名单会过期（2026-11-12 实历）：`/fd-quant`、`/fd-text-core`、`/fd-sentiment`
#: 早已装上门，却仍留在「可裸探」一侧——于是 `refresh_mcp_sources.py` 一跑就把三条
#: 正常在岗的服务报成「取数失败」并退出 1，看上去像三处故障。判据不是「以前探通过」，
#: 是**这次探到的 HTTP 码**：401/403 且 pod 活着、镜像与台账一致 = 鉴权门在岗。
_AUTH_GATED = {"fd-find-data-business-mcp", "facet-ops-mcp", "wanxing-ops-mcp",
               "wire-ops-mcp", "wire-build-mcp", "lex-ops-mcp", "fd-legal-search-mcp",
               "fd-quant", "fd-text-core", "fd-sentiment", "edu-catalog"}


def _init_and_list(url: str, timeout: float = 20.0) -> tuple[list[dict] | None, str]:
    cands = [url]
    base = url.rstrip("/")
    for u in (base, base + "/mcp", base + "/"):
        if u not in cands:
            cands.append(u)

    def rpc(payload: dict, session: str | None = None, url: str = ""):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        if session:
            req.add_header("Mcp-Session-Id", session)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            sid = r.headers.get("Mcp-Session-Id")
            body = r.read().decode("utf-8", "replace")
        if not body.strip():
            return {}, sid
        for line in body.splitlines():
            if line.startswith("data: "):
                return json.loads(line[6:]), sid
        return json.loads(body), sid

    notes = []
    for u in cands:
        try:
            init, sid = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                        "clientInfo": {"name": "refresh-sources", "version": "1"}}}, url=u)
            if "result" not in init:
                notes.append(f"{u}: initialize 无 result")
                continue
            rpc({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid, u)
            listed, _ = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, sid, u)
            tools = listed.get("result", {}).get("tools") or []
            if tools:
                return tools, "ok"
            notes.append(f"{u}: 0 工具")
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                return None, f"auth-gated({exc.code})"
            notes.append(f"{u}: HTTP {exc.code}")
        except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
            notes.append(f"{u}: {type(exc).__name__}")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"{u}: {type(exc).__name__}")
    return None, notes[0] if notes else "无候选"


def refresh(entry: str, only: bool) -> int:
    url, server_name, blurb = ENDPOINTS[entry]
    if entry in _AUTH_GATED:
        print(f"{entry:26} 跳过：工具面需凭据（不在裸探名单）")
        return 0
    tools, note = _init_and_list(url)
    if tools is None:
        print(f"{entry:26} 取数失败：{note}")
        return 1
    prev = SOURCES / f"{entry}.tools.json"
    old_names = []
    if prev.exists():
        try:
            old_names = [t["name"] for t in json.loads(prev.read_text(encoding="utf-8")).get("tools", [])]
        except Exception:  # noqa: BLE001
            old_names = []
    rows = sorted(
        ({"name": t.get("name", ""), "description": (t.get("description") or "").strip()} for t in tools),
        key=lambda r: r["name"],
    )
    doc = {"server_name": server_name, "description": blurb, "tags": [], "tools": rows}
    prev.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    new_names = [r["name"] for r in rows]
    added = [n for n in new_names if n not in old_names]
    gone = [n for n in old_names if n not in new_names]
    print(f"{entry:26} {len(new_names):3d} 工具 -> {prev.name}  新增{len(added)} 消失{len(gone)}"
          + (f"  新增: {', '.join(added[:6])}" if added else "")
          + (f"  消失: {', '.join(gone[:6])}" if gone else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default=None, help="只刷某个 entry")
    args = ap.parse_args()
    entries = [args.only] if args.only else list(ENDPOINTS)
    bad = 0
    for e in entries:
        if e not in ENDPOINTS:
            print(f"未知 entry: {e}", file=sys.stderr)
            bad += 1
            continue
        bad += refresh(e, bool(args.only))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
