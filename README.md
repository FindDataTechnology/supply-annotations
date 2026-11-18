# 供给注释（supply-annotations）

registry 在册 MCP 条目的多语言显示注释真源。壹座与谦面按 locale 渲染这里的
名字/一句话/工具说明；**运行时契约（registryName、工具名、参数 schema）零改动**。

- 跨仓契约（paas 如何装载）：`docs/mcp-annotation-source-requirements.md`
- OpenSpec change：`openspec/changes/add-mcp-supply-annotations/`

## 文件布局

```
supply-annotations/
  glossary.md                     # 术语表：同一概念 23 条共用一套译法
  mcp/<entry>.json                # 一条目一文件；<entry> == registry name（无前导斜杠）
  _sources/<entry>.tools.json     # 产出时的上游快照（只读输入，不入交付）
  dist/market-annotations.json    # 导出产物，交 paas（export.py 生成）
  validate.py                     # 形状 + 五语 + 覆盖 + 禁辞 + 一致性
  export.py                       # 汇总导出
```

## 条目文件形状

```json
{
  "version": 1,
  "server": "fd-quant",
  "annotation": {
    "human": {
      "zh": { "name": "量化计算", "summary": "一句话说明这是什么、给谁用。", "whenToUse": "什么时候该用它。" },
      "en": { "name": "...", "summary": "...", "whenToUse": "..." },
      "ja": { "name": "...", "summary": "...", "whenToUse": "..." },
      "es": { "name": "...", "summary": "...", "whenToUse": "..." },
      "fr": { "name": "...", "summary": "...", "whenToUse": "..." }
    },
    "canonical": { "brief": "面向智能体的精准一句话（≤300 字符）。" },
    "tools": {
      "<工具名逐字等于 tool_list.name>": {
        "human": {
          "zh": { "name": "通俗短名（≤60）", "summary": "这个工具做什么（≤200）。" },
          "en": { ... }, "ja": { ... }, "es": { ... }, "fr": { ... }
        },
        "canonical": { "brief": "..." }
      }
    },
    "provenance": { "source": "finddata-supply-annotations", "updatedAt": "2026-11-02" }
  }
}
```

规则（`validate.py` 强制）：

| 规则 | 说明 |
|---|---|
| 键对齐 | `server` == 文件名 == registry name；每个 `tools` 键必须逐字出现在 `_sources/<entry>.tools.json` 的 `tools[].name` 里 |
| 覆盖 | `tools` 键集合必须**等于**该条目的工具名集合（不缺不多） |
| 五语 | 每轨必须有 `zh` + `en` + `ja` + `es` + `fr`；server 级写 `whenToUse`，工具级不写 |
| 长度 | name ≤60、summary ≤200、whenToUse ≤160、canonical.brief ≤300（字符数，非字节） |
| 依据 | 只据 `_sources` 里的上游 description 与仓内 `tool-surface.json`，不发明能力；不得把写状态工具说成只读 |
| 禁辞 | 走 `docs/marketing/audit.py` 同款绝对化表述扫描 |

## 特殊（不注释）条目

2026-11-03 拍板（闭环 paas 回执 `docs/mcp-annotation-repo-source-receipt.md` §六）：

| registry name | 说明 |
|---|---|
| `fd-wire-cell-drillcust001` | 客户实例，group-restricted |
| `fd-wire-cell-pgauto001` | 客户实例，group-restricted |
| `fd-wire-cell-wiretester2` | 客户实例，group-restricted |

不注释的理由：受众为客户侧开发者，英文原文可读（原文渲染是设计行为，非欠账）；wire cell
按客户实例一条，键规则为 registry name 精确匹配，注释债随实例数累积；wire 引擎活跃开发、
工具面 churn 会使覆盖门（新增工具未注释即红）永续开火。

**A-lite 挂钩（触发条件）**：客户方明确提出需要中文/多语言注释时，先补 server 级
（3 条 × 5 语），工具级按曝光频次渐进。触发前不动。

## 用法

```bash
python3 supply-annotations/validate.py                 # 全量校验（含覆盖门）
python3 supply-annotations/validate.py --only fd-quant # 单条
python3 supply-annotations/export.py                   # 产出 dist/market-annotations.json
```

`--check-registry` 默认开启：从生产 registry 只读取 `tool_list` 做覆盖比对；
离线环境用 `--no-registry` 退回 `_sources` 快照（会打印来源标记）。


## 与 paas 交接的核对清单（task 4.3）

| 项 | 本仓约定 | paas 需求书对应节 |
|---|---|---|
| 文件名 | `dist/market-annotations.json`（导出产物，747KB） | §2.A |
| 顶层形状 | `{"version": 1, "entries": {<name>: {"annotation": {...}}}}` | §2.A |
| 键 | registry 条目 name（`pathToName(path)`，无前导斜杠） | §2.A |
| 值 | 既有 `annotation` 形状（human 五语 + canonical.brief + tools 按 leaf + provenance） | §2.A |
| 合并点 | paas `registry-bridge.js mapServer()` 一处（壹座与谦面共用） | §2.C |
| 出片 | `Dockerfile` COPY 一行；文件缺失 → 空表 + 原文渲染 | §2.D |
| 覆盖 | 23 条 / 587 工具，逐条 `validate.py` 对生产 registry 实时比对通过 | §3 |
