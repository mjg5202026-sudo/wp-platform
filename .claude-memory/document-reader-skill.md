---
name: document-reader-skill
description: document-reader-skill 项目概况 — Claude Code Skill，企业级文档解析工具
metadata:
  type: project
  lastUpdated: 2026-07-19
---

# document-reader-skill

## 项目定位
企业级文档解析工具，作为 Claude Code Skill 运行。读取 PDF、扫描件、图片、Word、Excel，自动判断是否需要 OCR，输出结构化 Markdown + JSON 元数据。

## 技术栈
- Python 3.12+（当前环境 3.8.10）
- PyMuPDF（PDF 解析）
- pytesseract（OCR 引擎）
- python-docx（Word）
- openpyxl（Excel）
- Pillow + opencv-python（图片预处理）
- pytest（79 个测试全部通过）

## 项目结构
```
document-reader-skill/
├── .claude/CLAUDE.md              # 项目规则
├── .claude/skills/document-reader/skill.json  # Skill 注册
├── config.py                      # 全局配置（无硬编码）
├── src/
│   ├── main.py                    # CLI 入口（typer + rich）
│   ├── reader.py                  # 核心编排器
│   ├── parsers/                   # PDF/图片/Word/Excel 解析器
│   ├── ocr/engine.py              # Tesseract 封装
│   ├── detectors/ocr_needed.py    # OCR 必要性判断
│   ├── converters/markdown.py     # Markdown 输出
│   ├── metadata/extractor.py      # 元数据提取
│   └── utils/                     # 日志、文件工具
├── tests/                         # 12 个测试文件，79 个测试
├── requirements.txt
└── README.md
```

## 外部 Skills（已安装）
- `addyosmani/agent-skills` 的 24 个 Prompt Skill（通过 `npx skills add` 安装）

## Git 仓库
- 远程: https://github.com/mjg5202026-sudo/wp-platform
- 当前分支: master
- 包含项目代码 + Claude 记忆备份 (.claude-memory/)

## 换电脑提醒
记忆文件在 `.claude-memory/` 中备份，需复制到:
`%USERPROFILE%\.claude\projects\d--soft-python-vscode-Daily-plan\memory\`
