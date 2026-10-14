# 内容保真、渲染与 PDF 核查

## 源内容覆盖

有源 TeX 时识别主文件、bibliography、宏、include、图像、算法和 listing。解压拒绝越界路径和符号链接；展开 input 限制在源目录，并跳过注释中的 input。不要粗暴去掉全文件的注释、宏或复杂环境。

Pandoc 转换可能静默丢内容；“没有 RawBlock”不证明完整。逐项对照：

- document 前定义的 abstract 是否进入正文；CJK 是否泄漏 UTF8gbsn。
- subfigure 的所有子图和每处出现位置；文件去重后的数量相同仍可能漏图。
- table/longtable 外层表数量、行列、合并单元格、每个 caption 和标签；嵌套表头单独计数。
- algorithm 的 For/If 控制流、条件和 State；可能无报错却只留下几行正文。
- lstinputlisting 的源码、caption 和标签；caption 可能仅在 AST 属性里而未翻译。
- bibliography、作者、脚注、附录、公式编号与跨引用。

移除 resizebox/adjustbox 包装时保留内部内容。cmidrule/cline 装饰不可解析成数字单元格。修复须对照原文定位后窄范围变换，不对所有论文套用单例正则。

处理 AST 保留可选 null 和数组位置，不能递归删除所有 None，尤其 Caption 等固定结构。完整保护数学节点，恢复标签及真实目标，不留下 [fig:...] 字面量。重复源标签做显式映射，不改变数学含义。

## HTML / MathJax 路线

无 TeX 编译器时可用 Pandoc 译后 AST 输出 HTML，用本地 MathJax 渲染，再由 Playwright Chromium/Edge 打印 PDF。发现当前可用的 Python、Node、Pandoc、Poppler、字体和浏览器路径，不硬编码旧目录或要求必须有 PyMuPDF。

MathJax 仅开启 `\\(...\\)` 与 `\\[...\\]`，避免美元价格被 `$` 误判为公式。Python 原始字符串示意：

```python
config = {"tex": {"inlineMath": [[r"\(", r"\)"]],
                  "displayMath": [[r"\[", r"\]"]],
                  "processEnvironments": True, "tags": "ams"}}
```

用 JSON 序列化配置，检查最终 JavaScript 的反斜线。已有 equation/align 环境不再次包同类环境，保留宏并检查 merror。

打印前等待 MathJax promise、`document.fonts.ready` 和图像加载；切换 print media 后测量。SVG 字形不一定出现在 PDF 文本提取中，必须检查实际 SVG 边界。MathJax min-width 可撑出长公式，仅 max-width 仍可能裁切。

越界时优先合理断行；需要缩放时整体缩放公式和编号，复查可读性。Chromium 可采用以下测量方式（页面固定为实际可打印宽度）：

```javascript
const span = /* 当前 .math.display */;
const box = span.querySelector('mjx-container');
const svg = box?.querySelector(':scope > svg');
if (svg && span.clientWidth) {
  const inherited = span.getBoundingClientRect().width / span.clientWidth;
  const natural = svg.getBoundingClientRect().width / inherited;
  if (natural > span.clientWidth + 2) {
    box.style.width = natural + 'px';
    box.style.zoom = span.clientWidth / natural;
  }
}
```

随后重新测量 svg 与 span 左右边界。zoom 依赖浏览器，不能视为跨引擎保证。表格过宽时调列宽、横页或拆分，不把整页字体缩至不可读。原始科研图直接使用，不用生成图片重绘数据。

## 完成判定

内容：检查章节与附录、表格数据和结构、图像位置、算法控制流、公式和引用目标，逐段翻译对齐。阅读总结辅助查漏，仍须核对原文目录及实际内容。

自动检查：无未恢复标记/明显乱码、缺图、MathJax 错误、越界和未解析引用；PDF 可打开，页数有效，文本和页边界合理。扫描图页无文本不等于空白页。

视觉检查：渲染全部页面成联系表浏览；封面、长公式、密集表、多子图、算法、长附录和可疑页放大核查。记录覆盖与遗留问题，不能只看第一页。重渲染用新目录或仅取当前页数，防止旧 PNG 混入。

分别记录阅读完成、翻译检查、渲染检查与视觉覆盖；未通过时保留草稿状态及续做材料。自动检查全过仍应说明机器辅助翻译和实际复核范围。
