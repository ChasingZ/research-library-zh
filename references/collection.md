# 资料搜集与版本管理

以机构官网、官方 GitHub、arXiv 作者记录、会议 proceedings 和期刊 DOI 页面为证据。搜索引擎帮助发现，官方页面用于确认。请求“至今”时实时检索并记录实际检索日期，分别注明首次发表、修订、正式出版日期；不根据模型记忆声称穷尽。

先建作品索引，再补 PDF。每条记录保存 work_id、title、type、authors、first_date、source_url、version、revision_date、venue、venue_status、license、local_source、source_sha256、priority、status、checked_at。未知信息用 null 或 unverified。预印本、会议录、期刊、技术报告、工程文档分别记录；不把 arXiv 收录写成期刊录用。模型卡、文档与相关论文互相链接。

通过 arXiv ID、DOI、规范化标题和作者交叉去重。会议版本与预印本有差异时保留对应关系；选定翻译版本后锁定版本，不能下载最新版却沿用旧版摘要、页数或标题。

每篇记录 collected → read → summarized → translating → rendered → checked → delivered，必要时注明阻塞原因。保存已读/已译章节和未解决问题，续做时不跳过附录或把草稿当完成稿。

交付说明检索截止日、范围、已核实/未核实项，链接阅读总结及译本。PDF 页数因重排可能增长，不以页数一致作为完整性证明。

## 打包清单

先完成实际核查，再据结果生成清单；禁止为通过工具而先填 verified=true。`package_verified.py` 输入：

```json
{
  "title": "核心论文中文资料",
  "checked_at": "实际核查日期",
  "files": [
    {
      "path": "paper/中文对照全文.pdf",
      "sha256": "文件的64位十六进制SHA256",
      "verified": true,
      "evidence": "paper/核查记录.json"
    },
    {
      "path": "paper/阅读总结.md",
      "sha256": "文件的64位十六进制SHA256",
      "verified": true,
      "evidence": "已对照原文逐节复核"
    }
  ]
}
```

路径相对于清单目录，不能指向目录外。evidence 为核查记录位置或具体说明，仅用于追溯，脚本不评估真实性。要交付核查记录时也须将该文件列入 files。仅打包显式列出的文件和清单，检查 ZIP CRC；成品版本与哈希应对应源索引。
