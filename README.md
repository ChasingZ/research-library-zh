# research-library-zh

**先读懂，再翻译。** 面向 Codex 的科研资料搜集、论文阅读与中文翻译 skill。

从研究机构或主题出发，建立可追溯的资料库；核心论文优先，先通读全文和附录、总结方法与实验、建立术语表，再逐段翻译、校核并交付中文 PDF。工作流来自 DeepSeek 核心论文资料整理实践，也适用于其他研究机构和主题。

## 工作流程

```text
资料搜集与版本去重
        ↓
核心论文排序
        ↓
通读正文、图表和附录
        ↓
阅读总结 + 术语表 + 疑点记录
        ↓
带入章节上下文，逐段翻译
        ↓
公式、数值、图表、引用与 PDF 视觉校核
        ↓
逐篇交付 + 进度记录 + 校验和与打包
```

阅读总结与全文译稿分别保存。总结为翻译提供上下文，不代替、压缩原文，也不将译者推断写成作者结论。

## 安装到 Codex

将本仓库放入个人 skills 目录；如果设置了 `CODEX_HOME`，使用其下的 `skills`，否则使用 `~/.codex/skills`。

**PowerShell：**

```powershell
$skillsRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex/skills' }
git clone https://github.com/ChasingZ/research-library-zh.git (Join-Path $skillsRoot 'research-library-zh')
```

**macOS / Linux：**

```bash
git clone https://github.com/ChasingZ/research-library-zh.git "${CODEX_HOME:-$HOME/.codex}/skills/research-library-zh"
```

安装目录若已存在，先检查已有版本，避免覆盖个人修改。在新的 Codex 会话中调用：

```text
使用 $research-library-zh 搜集 DeepSeek 的核心论文与技术文档。
每篇先通读全文、总结方法和实验、建立术语表，再翻译为中文对照 PDF。
第一篇通过检查后告诉我，然后继续其余论文。
```

已有本地论文时，也可以只执行阅读和翻译，不必重复搜集：

```text
使用 $research-library-zh 处理当前文件夹的论文。
先分别形成阅读总结和术语表，再按我给出的顺序翻译并检查 PDF。
```

## 文件与工具

| 文件 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | Codex 工作流入口 |
| [references/collection.md](references/collection.md) | 官方来源、去重、版本与交付清单 |
| [references/reading-and-translation.md](references/reading-and-translation.md) | 通读总结、术语、翻译与语义复核 |
| [references/rendering-and-qa.md](references/rendering-and-qa.md) | 内容保真、公式渲染与 PDF 核查 |
| [templates/reading-notes.md](templates/reading-notes.md) | 可复制的逐篇阅读总结模板 |
| [scripts/audit_units.py](scripts/audit_units.py) | 对齐翻译单元的占位符、可见数值与回显检查 |
| [scripts/package_verified.py](scripts/package_verified.py) | 校验显式清单并打包成品 |

这是一套由 Codex 执行的工作流与辅助工具，不是单命令自动翻译引擎。辅助 Python 脚本仅使用标准库，要求 Python 3.10+；搜集、翻译和 PDF 生成需要所在环境提供相应能力。源 TeX、Pandoc、MathJax、浏览器或 OCR 按输入和环境选择，不强制下载模型。

### 运行翻译单元检查示例

```bash
python scripts/audit_units.py examples/units.jsonl --report audit.json
```

占位符必须保留相同次数，可见数字应一致；问题报告返回非零退出码。脚本不会验证已冻结标记背后的原始数学对象，也不证明翻译语义正确、全文无遗漏。日期或单位的合法文字转换需记录复核依据。

### 打包经核查的文件

按 [清单格式](references/collection.md#打包清单) 填写实际文件路径、SHA256、核查状态与依据，然后运行：

```bash
python scripts/package_verified.py manifest.json deliverables.zip
```

只包含清单明确列出的文件和清单本身。输出存在时拒绝覆盖；缺少核查声明、路径越界或哈希不符时拒绝打包。核查声明由使用者据实际检查填写，工具不认证其真实性。

### 测试

```bash
python scripts/test_helpers.py
```

受限环境可以设置 `SKILL_TEST_TMPDIR` 指向可写的临时目录。GitHub Actions 在 Linux 和 Windows 上执行相同的辅助工具测试。

## 使用边界

- 译文写明原文版本、非官方性质及实际复核范围；机器辅助翻译不等于人工精校。
- 正文、附录、算法控制流、图表、公式与引用需对照原文检查；零告警不代表出版级质量。
- 本仓库不包含论文原文、译本、用户文件、API 密钥、模型权重或运行时。
- MIT 许可仅适用于本仓库的原创代码和说明，不授予第三方论文或数据的使用权。

## License

[MIT](LICENSE) © 2026 ChasingZ
