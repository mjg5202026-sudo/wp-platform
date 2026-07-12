# Document Reader Skill — 开发规范

## 项目定位
企业级文档解析工具，支持 PDF、扫描件、图片、Word、Excel 等格式，自动判断是否需要 OCR，输出结构化 Markdown，生成元数据。

## 技术栈
- Python 3.12+
- PyMuPDF（PDF 解析首选）
- PaddleOCR / Tesseract（图片 OCR 方案）
- python-docx（Word 解析）
- openpyxl（Excel 解析）
- pytest（测试框架）

## 编码规范
- ✅ 全部使用类型注解（PEP 484）
- ✅ 模块化设计，每个模块职责单一
- ✅ 不允许硬编码 —— 配置统一放 `config.py`
- ✅ 所有输出放 `output/` 目录
- ✅ 所有日志放 `logs/` 目录
- ✅ 异常链完整，每一层都要捕获并包装

## 工作流程
1. 每次新增功能 → 同步编写测试
2. 每次修改代码 → 运行 `pytest tests/`
3. 测试失败 → **必须先修复，再继续**
4. 提交前 → 确保全部测试通过

## Skill 注册
`.claude/skills/document-reader/skill.json` 定义了此 Skill 的触发条件和入口。

## 架构分层
```
src/
├── __init__.py
├── main.py              # CLI 入口
├── config.py            # 全局配置
├── detectors/           # 文件类型/OCR 检测
├── parsers/             # 各格式解析器
├── ocr/                 # OCR 引擎封装
├── converters/          # 格式转换 -> Markdown
├── metadata/            # 元数据提取
└── utils/               # 通用工具（日志、文件操作等）
```
