# 供给术语表（MCP 注释 + pack 副轨共用）

同一概念在 MCP 23 个条目与仓内 59 个 pack 源的五个语言里只允许一套译法。
产出注释或 pack `i18n` 副轨前先读这里；校验器对「禁用别名」做抽查。

## 1. 平台与供给

| 概念 | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| MCP 服务器 | MCP 服务 | MCP server | MCP サーバー | servidor MCP | serveur MCP |
| 工具 | 工具 | tool | ツール | herramienta | outil |
| 注册表 / 供给目录 | 供给目录 | registry | レジストリ | catálogo | registre |
| 智能体 | 智能体 | agent | エージェント | agente | agent |
| 集群 | 集群 | cluster | クラスタ | clúster | cluster |
| 岗位 | 岗位 | role | 役割 | rol | rôle |
| 上牌（对外暴露） | 上牌 | listed | 登録済み | publicado | publié |
| 草稿 | 草稿 | draft | 下書き | borrador | brouillon |
| 发布 | 发布 | publish | 公開 | publicar | publier |
| 证据 | 证据 | evidence | 根拠 | evidencia | preuve |
| 口径 | 口径 | methodology | 算出基準 | criterio | méthodologie |

## 2. 数据与指标

| 概念 | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| 指标 | 指标 | indicator | 指標 | indicador | indicateur |
| 时间序列 / 序列 | 序列 | series | 系列 | serie | série |
| 数据集 | 数据集 | dataset | データセット | conjunto de datos | jeu de données |
| 数据源 | 数据源 | source | データソース | fuente | source |
| 年度数据 | 年度数据 | annual data | 年次データ | datos anuales | données annuelles |
| 地区 / 省域 | 地区 | region | 地域 | región | région |
| 快照 | 快照 | snapshot | スナップショット | instantánea | instantané |
| 覆盖度 | 覆盖度 | coverage | カバレッジ | cobertura | couverture |
| 缺失值 | 缺失 | missing | 欠損 | faltante | manquant |

## 3. 金融与量化

| 概念 | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| 行情 | 行情 | market data | 市況 | cotización | cours |
| 回撤 | 回撤 | drawdown | ドローダウン | caída | repli |
| 波动率 | 波动率 | volatility | ボラティリティ | volatilidad | volatilité |
| 估值 | 估值 | valuation | バリュエーション | valoración | valorisation |
| 因子 | 因子 | factor | ファクター | factor | facteur |
| 组合 | 组合 | portfolio | ポートフォリオ | cartera | portefeuille |
| 决策账本 | 决策账本 | decision ledger | 意思決定台帳 | registro de decisiones | registre de décisions |
| 模拟交易 | 模拟交易 | paper trading | ペーパートレード | trading simulado | trading fictif |

## 4. 法务与文本

| 概念 | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| 法规 | 法规 | statute | 法令 | normativa | texte légal |
| 案例 | 案例 | case | 判例 | caso | affaire |
| 指导案例 | 指导案例 | guiding case | 指導性案例 | caso guía | affaire de référence |
| 裁判文书 | 裁判文书 | judgment | 判決文 | sentencia | jugement |
| 条款 | 条款 | clause | 条項 | cláusula | clause |
| 检索 | 检索 | search | 検索 | búsqueda | recherche |
| 正文 | 正文 | body text | 本文 | texto completo | texte intégral |

## 5. 柏讯 / 星研线

| 概念 | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| 需求单 | 需求单 | request | 依頼 | solicitud | demande |
| 订阅 | 订阅 | subscription | 購読 | suscripción | abonnement |
| 产物 | 产物 | artifact | 成果物 | artefacto | artefact |
| 更正 | 更正 | correction | 訂正 | corrección | correction |
| 内容流 | 内容流 | content stream | コンテンツフィード | flujo de contenido | flux de contenu |
| 画面 / 剧本 | 剧本 | screenplay | 脚本 | guion | scénario |

## 6. 写作纪律

1. `summary` 写「做什么 + 返回什么」，不写营销词（最强/唯一/第一/绝对/100%）。
2. 工具级 `name` 用 4–10 字的动作短语（如「读取序列」「按地区汇总」），不用英文 snake_case。
3. 工具级不写 `whenToUse`（与 summary 重复）；server 级必写。
4. 上游描述缺失时，只按工具名与参数猜其**可验证**的最小语义；猜不出就写「按名称推断，具体行为以服务端返回为准」——不许编造返回结构。
5. 五语等义，不增删信息；ja/es/fr 不引入英文原词做占位。

## 7. 禁用别名（出现即校验失败）

| 禁用 | 应用 |
|---|---|
| 舰队 | 集群 |
| 工具集 | 工具面 |
| 数据仓库（指本平台） | 数据集市 / 数据供给 |
| 接口文档（指 MCP 工具） | 工具说明 |

## 8. 品牌、岗位与平台词（pack 副轨共用）

**品牌英文名拍板（2026-11-02）**：全语言使用拉丁品牌名，不音译。既有 en 副轨
（`Wire Intel & Sentiment`、`Facet`、`Wanxing`）与此一致，无改写项。

| 概念 | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| 品牌·壹座 | 壹座 | Yizuo | Yizuo | Yizuo | Yizuo |
| 品牌·柏讯 | 柏讯 | Wire | Wire | Wire | Wire |
| 品牌·谦面 | 谦面 | Facet | Facet | Facet | Facet |
| 品牌·萬星 | 萬星 | Wanxing | Wanxing | Wanxing | Wanxing |
| 品牌·识律 | 识律 | Lex | Lex | Lex | Lex |
| 品牌·星研 | 星研 | Xingyan | Xingyan | Xingyan | Xingyan |
| 智能体构建器 | 智能体构建器 | Agent Builder | エージェントビルダー | Constructor de Agentes | Constructeur d'Agents |
| 巡检 | 巡检 | patrol | 巡回 | ronda | ronde |
| 主编 | 主编 | chief editor | 編集長 | editor jefe | rédacteur en chef |
| 投稿 | 投稿 | contribution | 投稿 | contribución | contribution |
| 构造师 | 构造师 | architect | アーキテクト | arquitecto | architecte |
| 报数 | 报数 | reporting | 報告 | informe | rapport |
| 拍板 | 拍板 | sign-off | 承認 | aprobación | validation |
| 遥测槽位 | 遥测槽位 | telemetry slot | テレメトリ・スロット | ranura de telemetría | emplacement de télémétrie |
| 情报 | 情报 | intelligence | 情報 | inteligencia | renseignement |
| 舆情 | 舆情 | public sentiment | 世論 | opinión pública | opinion publique |
| 蓝图 | 蓝图 | blueprint | ブループリント | plano | plan |
| 套件 | 套件 | suite | スイート | suite | suite |
| 市场 | 市场 | market | マーケット | mercado | marché |

## 9. pack 副轨纪律

1. 四副轨等义，不增删信息；ja/es/fr 不得用英文原串占位（专有名词与 §8 品牌名除外）。
2. 长度：`description` 与 zh 基字段比不超过 3:1；`name` ≤80、skill description ≤300、
   agent name ≤60、`fleet.members[].title` ≤60、`kpiSlots[].label` ≤60。
3. 内容字段（SKILL.md 正文、persona、promptTemplate）不翻；只翻 manifest 显示字段。
4. 舰队模板的 `fleet.i18n` 只翻队名、成员 title、KPI label；members/cadence/edges 结构不动。

## 10. 技能显示名（skill 注释域专用，2026-11-04）

registry 在册技能（262）与壹座文件技能（6）的 `human.*.name` 按本条例铸造。
逐技能名不进本表——本节给**命名纪律 + 后缀模式表 + 分域词根**，校验器对长度帽与
禁用别名做硬门，模式一致性做抽查。

### 10.1 命名纪律

1. zh 显示名 4–12 字，名词或动宾短语；保留行业惯用语（如「尽职调查」「穿透式监管」）。
2. slug 是运行身份，永不译；显示名不得夹 slug 原词（如 `cn-gov` 拆词后残留英文）。
3. 同一后缀在全部技能里只用一套译法（见 10.2）；同一前缀概念（如 civil/criminal）
   同样一套。校验器按后缀抽查不一致。
4. 五语等义；ja/es/fr 不用英文原串占位（品牌名与 §8 拉丁品牌词除外）。
5. 绝对化禁辞沿用 §6/§7 与 marketing audit 同款规则。

### 10.2 后缀模式表（slug 尾段 → 各语言后缀）

| slug 尾段 | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| -workflow | 流程 | workflow | ワークフロー | flujo de trabajo | flux de travail |
| -review | 审查 | review | 審査 | revisión | revue |
| -analysis | 分析 | analysis | 分析 | análisis | analyse |
| -detection | 识别 | detection | 検出 | detección | détection |
| -watch | 盯梢 | watch | ウォッチ | vigilancia | veille |
| -tracker / -tracking | 追踪 | tracker | トラッカー | seguimiento | suivi |
| -calculator | 计算器 | calculator | 計算ツール | calculadora | calculateur |
| -drafting | 起草 | drafting | 起草案 | redacción | rédaction |
| -generator | 生成器 | generator | ジェネレーター | generador | générateur |
| -check / -checks | 核验 | check | チェック | verificación | contrôle |
| -extraction | 提取 | extraction | 抽出 | extracción | extraction |
| -mapping | 梳理 | mapping | マッピング | mapeo | cartographie |
| -comparison | 比对 | comparison | 比較 | comparación | comparaison |
| -forecast / -projection | 预测 | forecast | 予測 | previsión | prévision |
| -screening / -screener | 筛选 | screening | スクリーニング | cribado | filtrage |
| -backtest / -protocol | 回测 | backtest | バックテスト | backtest | backtest |
| -model | 模型 | model | モデル | modelo | modèle |
| -valuation | 估值 | valuation | バリュエーション | valoración | valorisation |
| -memo / -note | 备忘 | memo | メモ | nota | note |
| -plan | 方案 | plan | プラン | plan | plan |
| -summary | 摘要 | summary | 要約 | resumen | résumé |

### 10.3 分域词根（legal / wire / finance 高频概念）

| 概念 | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| 民事 | 民事 | civil | 民事 | civil | civil |
| 刑事 | 刑事 | criminal | 刑事 | penal | pénal |
| 劳动 | 劳动 | labor | 労働 | laboral | travail |
| 合同 | 合同 | contract | 契約 | contrato | contrat |
| 诉讼 | 诉讼 | litigation | 訴訟 | litigio | contentieux |
| 仲裁 | 仲裁 | arbitration | 仲裁 | arbitraje | arbitrage |
| 合规 | 合规 | compliance | コンプライアンス | cumplimiento | conformité |
| 尽职调查 | 尽调 | due diligence | デューデリジェンス | diligencia debida | diligence raisonnable |
| 政策 | 政策 | policy | 政策 | política | politique |
| 监管 | 监管 | regulation | 規制 | regulación | régulation |
| 产业链 | 产业链 | industry chain | 産業チェーン | cadena industrial | chaîne industrielle |
| 财报 | 财报 | earnings | 決算 | resultados | résultats |
| 宏观 | 宏观 | macro | マクロ | macro | macro |
| 轮动 | 轮动 | rotation | ローテーション | rotación | rotation |
| 事件 | 事件 | event | イベント | evento | événement |
| 冲击 | 冲击 | shock | ショック | choque | choc |
| 缺口 | 缺口 | gap | ギャップ | brecha | écart |
| 因子 | 因子 | factor | ファクター | factor | facteur |
| 提纲 / 面试提纲 | 提纲 | outline | 概要（按条目定） | esquema | plan d'examen |

> 10.3 最后一行为「按条目定」的例子：无通用后缀映射的概念，逐条在批注阶段定名
> 并回填本表（治理纪律：同一个英文词根第二次出现时必须已在本表有行）。

### 10.4 壹座文件技能定名（已定案）

| slug | zh | en | ja | es | fr |
|---|---|---|---|---|---|
| computer-file-system | 文件系统操作 | File system operations | ファイルシステム操作 | Operaciones del sistema de archivos | Opérations du système de fichiers |
| computer-process | 进程管理 | Process management | プロセス管理 | Gestión de procesos | Gestion des processus |
| computer-shell | Shell 命令执行 | Shell command execution | シェルコマンド実行 | Ejecución de comandos shell | Exécution de commandes shell |
| crm-desk-reception | 客服台接待 | CRM desk reception | カスタマー受付 | Recepción de mostrador CRM | Réception CRM |
| example-skill | 示例技能 | Example skill | サンプルスキル | Habilidad de ejemplo | Compétence d'exemple |
| platform-output-contract | 平台产物契约 | Platform output contract | プラットフォーム出力契約 | Contrato de salida de plataforma | Contrat de sortie de plateforme |

