---
name: patent-disclosure-skill
description: 中国专利交底书生成流程：扫描项目材料、挖掘专利点、检索现有技术、按用户提供的《专利交底书模板.docx》直接填充表格式技术交底书，生成清晰附图并保留可编辑源文件。
version: 2.1.0-docx-drawings
user-invocable: true
argument-hint: [可选：项目路径、技术主题、交底书模板 docx 路径]
allowed-tools: Read, Write, Edit, Grep, Glob, WebSearch, Bash
---

# 专利交底书生成（模板版）

本技能的目标是输出与用户提供的《专利交底书模板.docx》一致的技术交底书。交付物必须优先为直接填充后的 `.docx`；如有附图，应同时生成高清 PNG 插入 Word，并保留 DOT/SVG 等可编辑或矢量源文件。必要时同时保留结构化 `payload.json` 作为可追溯中间稿。

## 触发条件

用户提到以下任意内容时启用：专利交底书、技术交底书、专利点、专利挖掘、查新、现有技术、发明内容、实施方式、附图、欲保护点。

若用户给出已有交底书或模板，则以用户提供文件为格式和风格的最高优先级依据。

## 工作原则

1. **模板优先**：不得默认输出原仓库的“注意事项 / 一、二、三、四、五、六”通用 Markdown 六章结构；必须按《专利交底书模板.docx》的表格字段组织内容。
2. **参考样稿优先**：用户提供的已完成交底书是写作风格依据。内容组织应接近样稿：先填文头、关键词、检索式、检索结果、相关性分析，再写摘要、技术领域、背景技术、发明内容、实施方式、替代方案、附图、技术创新点。
3. **不空泛**：实施方式必须写可实施步骤、关键参数、数据流或控制逻辑；不能只写功能愿景。
4. **至少两个实施方式**：除非用户明确要求简版，所有的实施方式栏至少包含“实施方式一”和“实施方式二”。方法类可按 S1-Sn 展开；系统/设备类需结合模块和附图标记说明。
5. **附图说明规范**：附图统一用“图1、图2、图3……”；图说明用“图1为……图”的句式。代表性附图可以是流程图、系统架构图或核心模型图。附图图片本体必须采用白底、黑色边框、黑色文字、黑色箭头的简洁流程卡片风格；根据实际关系选择纵向、横向或多层堆叠排布；图片内部不得写“图1”“图2”等图号、图题或描述性标题，图号和图题只写在 Word 正文图注/附图说明中。
6. **检索结果写入模板栏**：现有技术检索分为“期刊或书籍等现有技术检索”和“中国专利检索”。链接和原始检索记录可以保留在查新笔记或 payload 的 `prior_art_records` 中，模板正文以代理人可读的概括为主。
7. **自检不写入正文**：自检结果只用于修改交付稿，不得在交底书正文末尾添加“自检清单”“免责声明”“技能仓库说明”等元信息。

## 工具与文件

- `prompts/intake.md`：收集案件边界、联系人、模板路径。
- `prompts/project_scan.md`：扫描项目材料、已有交底书、设计文档和源码。
- `prompts/patent_points_analyzer.md`：挖掘和筛选专利点，可沿用原仓库版本。
- `prompts/prior_art_search.md`：现有技术检索，并生成模板栏所需的检索结果和相关性分析素材。
- `prompts/disclosure_preview.md`：生成前预览，结构必须贴合模板字段。
- `prompts/disclosure_builder.md`：生成完整 payload 和正文内容。
- `prompts/template_reference.md`：模板字段、写法和样稿风格要求。
- `prompts/disclosure_self_check.md`：定稿前内部检查。
- `tools/fill_disclosure_template.py`：将 payload 填入《专利交底书模板.docx》。
- `tools/render_disclosure_drawings.py`：从 payload 的 `drawings` 生成 DOT/SVG/PNG 附图。
- `tools/build_disclosure_docx.py`：一键生成附图、填充 DOCX 模板、打包附图源文件。

## 主流程

1. Read `prompts/intake.md`，确认技术主题、联系人、模板路径、是否已有参考交底书。
2. Read `prompts/project_scan.md`，扫描项目文档和已有交底书。若有 `.docx` / `.pptx`，先转换或直接读取表格、图片、正文后再分析。
3. Read `prompts/patent_points_analyzer.md`，形成候选专利点并确定本次发明名称。
4. Read `prompts/prior_art_search.md`，完成现有技术检索；将结果压缩为模板两栏和“相关性分析”。
5. Read `prompts/disclosure_preview.md`，输出模板字段级预览。
6. Read `prompts/disclosure_builder.md` 与 `prompts/template_reference.md`，生成完整 payload。
7. 使用 `tools/build_disclosure_docx.py` 一键生成附图、填充用户提供的模板 `.docx`，并可打包附图源文件。
8. Read `prompts/disclosure_self_check.md`，对 `.docx` 内容、图号、附图源文件和模板字段进行一致性检查；修改 payload 或 DOCX 后再交付。

## 输出命名

默认输出：`{发明名称}-专利交底书.docx`。

如用户要求多版本留档，可追加时间戳：`{发明名称}-专利交底书_{YYYYMMDDHHmmss}.docx`。

## 交付要求

- 必交：填充后的 `.docx`。
- 建议交付：同名 `payload.json` 或 `payload.with_drawings.json`，便于后续迭代。
- 如有附图，建议交付：`附图源文件.zip`，包含 `.dot`、`.svg`、`.png`。
- Word 内插入 PNG 以保证兼容性；可编辑性通过 `.dot`/`.svg` 源文件保证。

交付说明中只列文件和修改摘要，不输出大段正文重复内容。
