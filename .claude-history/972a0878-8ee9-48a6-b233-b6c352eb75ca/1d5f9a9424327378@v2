# Document Reader Skill

> 企业级文档解析工具，基于 Claude Code Skill 体系打造。

## 功能

| 格式 | 方式 | 引擎 |
|------|------|------|
| PDF（文字版） | 直接提取 | PyMuPDF |
| PDF（扫描件） | OCR 识别 | PaddleOCR → Tesseract（降级） |
| PNG / JPG | OCR 识别 | PaddleOCR → Tesseract（降级） |
| Word (.docx) | 结构化提取 | python-docx |
| Excel (.xlsx) | 表格提取 | openpyxl |
| 输出 | Markdown + 元数据 JSON | — |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 解析文档
python src/main.py input/sample.pdf

# 指定输出目录
python src/main.py input/sample.pdf --output ./my_output

# OCR 模式（强制）
python src/main.py input/scan.png --ocr-mode force
```

## 项目结构

```
document-reader-skill/
├── .claude/
│   ├── CLAUDE.md              # 项目规则
│   └── skills/document-reader/
│       └── skill.json         # Skill 注册
├── src/                        # 业务代码
├── tests/                      # 测试
├── examples/                   # 示例脚本
├── output/                     # 输出目录
├── config.py                   # 配置（根目录）
└── requirements.txt            # 依赖
```

## 输出结构

```
output/
└── 2026-07-04_14-30-00_sample/
    ├── content.md              # 解析后的 Markdown
    ├── metadata.json           # 文档元数据
    └── logs/                   # 处理日志
```

## 开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行全部测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_parsers.py -v
```

## 许可证

MIT
