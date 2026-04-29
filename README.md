# xhs-agent-content-pipeline

一个面向求职作品集的“小红书内容运营 AI Agent 自动化系统”Demo。项目把内容采集、数据清洗、爆款分析、改写策略、二创生成、质量检查和表格导出串成一条完整管线，用于展示 AI Agent、自动化采集、结构化数据处理、大模型分析、多 Agent 协作和内容生成能力。

> 本项目用于个人学习、作品集展示和合规的登录后数据整理测试。不要绕过验证码、登录限制、平台风控或反爬机制。

## 核心痛点

传统内容运营流程依赖人工搜索、复制、分析和改写，常见问题包括：

- 爆款笔记搜索和整理耗时长；
- 标题、正文、标签、互动数据复制容易出错；
- 爆款原因依赖经验，难以沉淀成可复用方法论；
- 对标改写和二创生产效率低；
- 内容生成缺少自动质检；
- 数据分散在网页、表格和文本中，缺少统一流程。

## 核心功能

- **Crawler**：基于 Playwright 的采集接口设计，Demo 默认使用 mock 数据跑通流程。
- **Processor**：清洗标题、正文、标签，标准化互动数据并计算 `engagement_score`。
- **Analysis Agent**：分析标题钩子、用户痛点、情绪价值、正文结构、标签策略、爆款原因和可复用写法。
- **Rewrite Agent**：生成目标人群、内容角度、标题方向、正文结构和差异化创新点。
- **Creation Agent**：输出二创标题、正文、标签、图片提示词和发布建议。
- **Quality Agent**：用规则检查标题长度、正文语气、标签数量和内容完整性。
- **Exporter**：导出 JSON 和 CSV，方便面试展示或进一步分析。

## 技术架构

```text
Mock/Playwright Crawler
        |
        v
Data Processor
        |
        v
Analysis Agent -> Rewrite Agent -> Creation Agent -> Quality Agent
        |
        v
JSON / CSV Export
```

技术栈：

- Python 3.10+
- Playwright
- OpenAI 兼容接口
- python-dotenv
- 标准库 CSV / JSON / logging

## 多 Agent 协作流程

本项目不是简单文案生成工具，而是一个多 Agent 协作的内容运营自动化管线。每个 Agent 只负责一个明确任务：

- `AnalysisAgent`：从原始爆款笔记中抽取运营洞察；
- `RewriteAgent`：把洞察转化为可执行的二创策略；
- `CreationAgent`：根据原文、分析和策略生成新内容；
- `QualityAgent`：对生成结果做发布前质检。

前一个 Agent 的结构化输出会成为后一个 Agent 的输入，形成可追踪、可调试、可扩展的长链推理流程。

## 长链推理说明

单次文案生成很难保证稳定质量。本项目采用“采集 -> 清洗 -> 分析 -> 策略 -> 创作 -> 质检”的分阶段推理：

1. 先把混乱的网页或 mock 数据清洗成统一 schema；
2. 再从爆款内容中抽取可复用方法论；
3. 再将方法论转成适合新目标人群的改写策略；
4. 最后生成二创内容，并通过规则质检减少低质量输出。

这种设计让每一步都有中间产物，便于排查问题，也便于未来替换为更强模型或接入人工审核。

## 项目结构

```text
xhs-agent-content-pipeline/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py
├── config.py
├── data/
│   └── mock_notes.json
├── outputs/
│   └── .gitkeep
└── src/
    ├── crawler/
    │   ├── __init__.py
    │   ├── mock_crawler.py
    │   └── xhs_crawler.py
    ├── processor/
    │   ├── __init__.py
    │   └── cleaner.py
    ├── agents/
    │   ├── __init__.py
    │   ├── base_agent.py
    │   ├── analysis_agent.py
    │   ├── rewrite_agent.py
    │   ├── creation_agent.py
    │   └── quality_agent.py
    ├── exporters/
    │   ├── __init__.py
    │   └── csv_exporter.py
    └── utils/
        ├── __init__.py
        └── logger.py
```

## 安装方式

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

如果只运行 mock 模式，不安装 Chromium 也可以完成主流程。

## 环境变量配置

复制配置模板：

```bash
copy .env.example .env
```

`.env` 示例：

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

支持任何 OpenAI 兼容接口：

- DeepSeek：`OPENAI_BASE_URL=https://api.deepseek.com/v1`，模型可配置为 `deepseek-chat`；
- 豆包或其他兼容服务：填写服务商提供的 Base URL 和模型名；
- 未配置 `OPENAI_API_KEY` 时，系统会自动切换到 mock LLM 模式，保证 Demo 可直接运行。

## 运行方式

一键运行完整流程：

```bash
python main.py --mode mock
```

Windows 如果 `python` 命令不可用，可以使用：

```bash
py main.py --mode mock
```

默认情况下，`--mode mock` 会同时使用 mock 数据和 mock LLM，不会请求远程模型，所以适合面试演示和离线运行。

如果要使用 `.env` 中配置的真实 OpenAI 兼容模型：

```bash
python main.py --mode mock --llm-mode auto
```

指定输出目录：

```bash
python main.py --mode mock --output-dir outputs
```

真实采集接口预留：

```bash
python scripts/save_xhs_login.py
python main.py --mode live --keyword "护肤" --limit 5
```

`save_xhs_login.py` 会打开可见浏览器，请你手动登录小红书，登录完成后回到终端按 Enter 保存 `auth/xhs_storage_state.json`。该文件包含 cookie，已经被 `.gitignore` 忽略，不能提交到 GitHub。

`live` 模式仅用于登录后个人学习测试，不包含绕过验证码、风控或登录限制的逻辑。页面结构可能随平台更新变化，如果采集不到结果，需要根据实际页面调整选择器。

## 输出结果示例

运行后会在 `outputs/` 目录生成：

- `pipeline_results_YYYYMMDD_HHMMSS.json`
- `pipeline_results_YYYYMMDD_HHMMSS.csv`

CSV 字段包括：

- 原标题、原正文、原标签；
- 点赞数、收藏数、评论数、互动分；
- 爆款分析；
- 改写策略；
- 二创标题、二创正文、二创标签；
- 质检结果。

示例内容：

```text
原标题: 熬夜党早八快速消肿的 5 个小习惯
爆款分析: 标题用明确人群和可量化收益建立点击动机...
二创标题: 打工人早八不垮脸：5 个快速恢复状态的小动作
质检结果: passed=true
```

## 后续优化方向

- 接入合规的登录态采集和人工确认队列；
- 增加截图、OCR 和多模态图片分析；
- 引入向量库沉淀爆款案例库；
- 加入任务编排、重试和 Agent 记忆；
- 增加人工审核 UI；
- 对接 Notion、飞书、多维表格或 Google Sheets；
- 增加单元测试和 CI。

## 求职展示价值

这个项目可以体现：

- 能把真实业务流程拆成可执行的 AI Agent 管线；
- 熟悉 Playwright 自动化采集和 mock-first Demo 设计；
- 能处理结构化数据清洗、评分和导出；
- 能封装 OpenAI 兼容模型调用并设计降级方案；
- 理解多 Agent 协作、长链推理和中间结果可追踪的重要性；
- 具备将 AI 能力产品化、工程化和可演示化的能力。

