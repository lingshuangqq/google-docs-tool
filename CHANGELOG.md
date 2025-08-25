# 更新日志

本项目所有重要的更改都将记录在此文件中。

本日志的格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，且本项目遵循[语义化版本](https://semver.org/spec/v2.0.0.html)规范。

## [1.0.0] - 2025-08-21

### 新增 (Added)

- **初始版本发布**：Google Docs Markdown 上传工具首次发布。

- **核心功能**
    - 创建了一个健壮的 Python 工具 (`google_docs_tool.py`)，用于与 Google Docs API 交互。
    - 使用 FastAPI (`mcp_server.py`) 实现了客户端/服务器架构，将工具函数封装为稳定的 API。
    - 开发了灵活的客户端脚本 (`client.py`, `run_markdown_append.sh`)，用于通过命令行与服务器交互。

- **Markdown 到 Google Docs 的转换引擎**
    - 实现了一个解析器，可将 Markdown 文本转换为带格式的 Google Docs 内容。
    - 新增了对多级标题 (`#`, `##`, `###`) 的支持。
    - 新增了对**粗体**文本 (`**text**`) 的支持，包括处理同一行内的多个粗体段落。
    - 新增了对换行符 (`
`) 的支持，以创建段落分隔。
    - 初步支持了从 Markdown 表格语法创建正确尺寸的空表格框架。

- **专业的项目结构**
    - 将代码库组织成一个专业的 Python 包结构，包含 `src`, `credentials`, `script`, 和 `test` 目录。
    - 创建了 `pyproject.toml` 和 `requirements.txt` 文件来定义项目及其依赖，并由 `uv` 管理。
    - 实现了完整的 `.gitignore` 文件，以从版本控制中排除敏感和不必要的文件。

- **全面的测试体系**
    - 开发了使用模拟（mocking）的本地单元测试 (`test_local_google_docs_tool.py`)，用于快速、离线的逻辑验证。
    - 开发了可由环境变量激活的在线集成测试 (`test_integration_google_docs_tool.py`)，用于测试与真实 Google API 的交互。
    - 创建了一个带有命令行界面的主测试运行脚本 (`run_tests.sh`)，以方便地执行不同的测试套件。

- **项目文档**
    - 创建了详细的 `README.md`，包含项目概览、架构图，以及完整的安装、使用和测试说明。
    - 创建了此 `CHANGELOG.md` 文件，用于追踪项目版本历史。
