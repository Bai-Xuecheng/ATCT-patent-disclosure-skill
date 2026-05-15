# 技术交底书生成（Step 7，模板版）

## 目标

生成一个完整的 `payload.json`，再用 `tools/build_disclosure_docx.py` 一步完成：生成清晰附图、保留可编辑附图源文件、填充用户提供的《专利交底书模板.docx》。最终交底书必须与用户参考样稿的表格结构一致。

## 禁止输出的旧结构

不得生成下列原通用模板标题：

- 注意事项
- 一、介绍相关技术背景……
- 二、针对上述缺点……
- 三、本发明技术方案的详细阐述
- 四、与现有技术相比……
- 五、本发明的技术关键点……
- 六、其它

本版只使用《专利交底书模板.docx》中的字段。

## 生成步骤

### 1. 形成发明名称

发明名称应体现：核心技术手段 + 应用对象 + 权利要求类型。示例：

- 一种基于多传感器感知的低黏着风险在线评估方法
- 基于动态参数的列车安全防护方法
- 基于 Atlas 300I Pro 的无人机视频自适应推理与空间联动告警方法、设备及介质

### 2. 生成关键词和检索式

关键词 3–5 个，中英文对应。检索式写入 payload：

- `search_formula_cn` 以 `中文：` 开头；
- `search_formula_en` 以 `英文：` 或 `English:` 开头；
- 使用 `AND / OR`；
- 体现同义词和应用场景。

### 3. 写“相关技术检索结果”

分别生成：

- `prior_art_literature`：期刊、书籍、标准、公开资料检索结果；
- `prior_art_patents`：中国专利检索结果。

写法应压缩、可读，不要堆表格。可包含专利号、论文题名和方向概括。

### 4. 写“相关性分析”

`relevance_analysis` 采用“概括区别 + 具体差异”结构，至少 2 段。

必须回答：现有技术没有同时公开哪些组合技术特征，本发明为什么形成一个整体闭环。

### 5. 写摘要和技术领域

`abstract` 为 1 段，包含“本发明公开一种……”；不要分条。

`technical_field` 为 1 句或 1 段，包含“本发明/本申请涉及……技术领域，具体涉及……”。

### 6. 写背景技术

`background` 为连续正文，通常 4–8 段。结构：行业背景 → 现有技术 → 缺陷 → 本方案必要性。

### 7. 写发明内容

`purpose_and_effect` 必须分为：

```text
一、要解决的技术问题
1. ...
2. ...

二、有益的技术效果
1. ...
2. ...
```

不要只写“提高效率、降低成本”这类空泛效果，要对应技术手段。

### 8. 写所有的实施方式

`embodiments` 至少包含两个实施方式。

推荐结构：

```text
实施方式一：……方法
如图1和图2所示，本实施方式包括以下步骤。
S1，……。
S2，……。
S3，……。
...

实施方式二：……设备/系统/介质
如图3所示，本实施方式包括……模块。……
```

若用户参考样稿以“步骤一、步骤二”呈现，可沿用该风格，但仍须至少覆盖两个实施方式或多个优选实现。

### 9. 写可替代方案

`alternatives` 没有替代方案时写“无”。有替代方案时：

```text
替代方案一：……。优点是……，缺点是……。
替代方案二：……。优点是……，缺点是……。
```

### 10. 写附图和保护点

`drawings` 至少给出图1。建议图1为系统整体架构图或核心流程图。

附图图片风格必须统一为：白底、黑色边框、黑色文字、黑色箭头，不使用彩色填充、渐变、阴影、圆角装饰或复杂背景。流程卡片排布应根据实际技术关系选择：

- 线性步骤、时序流程：使用纵向自上而下排布；
- 数据流水线、输入到输出链路：使用横向从左到右排布；
- 系统架构、并行模块、分层控制链路：使用多层堆叠或分层 rank 排布。

图片内部不得写“图1”“图2”等图号、图题或描述性标题，也不得写“图1为……图”。图号和图题只保留在 payload 的 `no`、`title` 字段以及 Word 正文的图注/附图说明中。

为保证附图清晰且可编辑，优先在 `drawings` 中给出 `nodes` / `edges` 或 `dot`，不要只写图片占位。工具会生成：

- `.dot`：可编辑源文件；
- `.svg`：矢量图；
- `.png`：插入 Word 的高清兼容图。

推荐 `drawings` 写法：

```json
{
  "no": "图1",
  "title": "系统整体架构图",
  "layout": "vertical",
  "nodes": [
    {"id": "A", "label": "数据采集模块"},
    {"id": "B", "label": "特征处理模块"},
    {"id": "C", "label": "模型推理模块"},
    {"id": "D", "label": "结果输出模块"}
  ],
  "edges": [["A", "B"], ["B", "C"], ["C", "D"]]
}
```

复杂图可以直接给 Graphviz DOT：

```json
{
  "no": "图2",
  "title": "核心控制流程图",
  "dot": "digraph G { graph [rankdir=TB, bgcolor=\"#FFFFFF\", dpi=260]; node [shape=box, style=\"filled\", fillcolor=\"#FFFFFF\", color=\"#000000\", fontcolor=\"#000000\", fontname=\"Noto Sans CJK SC\"]; edge [color=\"#000000\", fontcolor=\"#000000\"]; A [label=\"输入\"]; B [label=\"处理\"]; A -> B; }"
}
```

`protection_points` 用编号列出 4–8 点，每点以“保护……”开头或包含可保护技术特征。

## payload 输出要求

生成 JSON 时必须是有效 JSON，不要带 Markdown 围栏。字段如下：

```json
{
  "meta": {
    "编号": "",
    "撰写人": {"姓名": "", "手机": "", "邮箱": "", "座机": ""},
    "技术问题联系人": {"姓名": "", "手机": "", "邮箱": "", "座机": ""}
  },
  "title": "",
  "keywords_cn": [],
  "keywords_en": [],
  "search_formula_cn": "",
  "search_formula_en": "",
  "prior_art_literature": "",
  "prior_art_patents": "",
  "relevance_analysis": "",
  "abstract": "",
  "representative_figure": "",
  "technical_field": "",
  "background": "",
  "purpose_and_effect": "",
  "embodiments": "",
  "alternatives": "无",
  "drawings": [],
  "protection_points": "",
  "prior_art_records": []
}
```

## 生成附图并填充 DOCX

payload 完成后优先执行一键构建命令。该命令会先把 `drawings` 渲染为高清 PNG，并保留 DOT/SVG 源文件，然后把内容直接填入用户的 DOCX 表格模板：

```bash
python3 tools/build_disclosure_docx.py \
  --template "专利交底书模板.docx" \
  --payload "payload.json" \
  --output "{发明名称}-专利交底书.docx" \
  --drawings-dir "{发明名称}-drawings" \
  --updated-payload "{发明名称}-payload.with_drawings.json" \
  --zip-drawing-sources "{发明名称}-附图源文件.zip"
```

只有在不需要生成附图源文件时，才单独使用 `tools/fill_disclosure_template.py`。

## 交付前检查

- DOCX 是否仍是表格式交底书；
- 每个模板栏是否已填；
- “所有的实施方式”是否至少两个；
- “附图”和正文中图号是否一致；
- 无技能仓库脚注、免责声明、自检清单。
