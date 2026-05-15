# 专利交底书 Skill 覆盖包（DOCX 直填 + 清晰附图版）

本覆盖包用于把 `handsomestWei/patent-disclosure-skill` 的通用 Markdown 六章式交底书，改为用户提供的《专利交底书模板.docx》表格式交底书，并默认直接填充 DOCX 模板。附图采用“高清 PNG 插入 Word + DOT/SVG 源文件留存”的方式，兼顾清晰度和可编辑性。

## 替换方式

在原仓库根目录执行：

```bash
# 假设本覆盖包目录为 /path/to/patent-disclosure-skill-docx-drawings-overlay
cp /path/to/patent-disclosure-skill-docx-drawings-overlay/SKILL.md ./SKILL.md
cp /path/to/patent-disclosure-skill-docx-drawings-overlay/prompts/*.md ./prompts/
cp /path/to/patent-disclosure-skill-docx-drawings-overlay/tools/fill_disclosure_template.py ./tools/
cp /path/to/patent-disclosure-skill-docx-drawings-overlay/tools/render_disclosure_drawings.py ./tools/
cp /path/to/patent-disclosure-skill-docx-drawings-overlay/tools/build_disclosure_docx.py ./tools/
cp /path/to/patent-disclosure-skill-docx-drawings-overlay/tools/example_disclosure_payload.json ./tools/
```

如需保留原仓库，可先备份：

```bash
cp SKILL.md SKILL.md.bak
cp prompts/disclosure_builder.md prompts/disclosure_builder.md.bak
cp prompts/template_reference.md prompts/template_reference.md.bak
cp prompts/disclosure_preview.md prompts/disclosure_preview.md.bak
cp prompts/prior_art_search.md prompts/prior_art_search.md.bak
cp prompts/intake.md prompts/intake.md.bak
```

## 使用方式

1. 把用户提供的 `专利交底书模板.docx` 放在项目目录或交底书输出目录。
2. 让 Agent 先按 `prompts/disclosure_builder.md` 生成结构化 `payload.json`。
3. 用 `tools/fill_disclosure_template.py` 填入模板：

```bash
python3 tools/fill_disclosure_template.py \
  --template "专利交底书模板.docx" \
  --payload "payload.json" \
  --output "案件名称_技术交底书.docx"
```

4. 如有代表性附图或正式附图，在 payload 中填 `representative_figure` 和 `drawings[].path`，脚本会插入到模板相应区域。

## 本版和原 Skill 的核心差异

- 以《专利交底书模板.docx》的 26 行表格为唯一输出骨架。
- 不再生成“注意事项 / 一、二、三、四、五、六”的通用 Markdown 正文。
- “相关技术检索结果”分为“期刊或书籍等现有技术检索”和“中国专利检索”两个模板栏。
- “相关性分析”必须直接写区别技术点。
- “摘要 + 代表性附图”必须在同一表格区块中呈现。
- “所有的实施方式”至少两个实施方式；方法类按“实施方式一 / S1-Sn”或“步骤一 / 步骤二”展开。
- “可替代的技术方案”没有时写“无”。
- “附图”区域使用“图1、图2……”及“图1为……图”的统一说明。
- 附图默认生成高清 PNG 插入 Word，同时保留 `.dot` / `.svg` 源文件，便于二次编辑。
- “着重保护的技术创新点”用编号列出要保护的核心技术特征。

## 附图生成说明

`tools/build_disclosure_docx.py` 会读取 payload 中的 `drawings`：

- 如果附图项含 `nodes` / `edges`，会自动生成流程图或模块图；
- 如果附图项含 `dot`，会按 Graphviz DOT 源码渲染；
- 如果附图项只有 `path`，会直接插入已有图片；
- 如果系统没有安装 Graphviz，会保留 `.dot` 源文件，但无法自动生成 PNG/SVG，需要先安装 Graphviz 或手工提供图片路径。

推荐在 Agent 生成 payload 时把图画成结构化节点和连线，而不是只描述“此处放流程图”。
