# 更新日志

本项目所有重要的更改都将记录在此文件中。

本日志的格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，且本项目遵循[语义化版本](https://semver.org/spec/v2.0.0.html)规范。

## [1.1.0] - 2025-08-25

### 新增 (Added)

- **新增 OAuth 2.0 用户鉴权模式**：除了原有的服务账号，现在工具的使用者可以通过浏览器登录自己的 Google 账号进行授权，以个人身份操作文档。
- **新增动态文档创建功能**：通过集成 Google Drive API，实现了在用户的云端硬盘根目录或指定文件夹下，动态创建新的 Google 文档。
- **新增 `clear` (清空) 命令**：为客户端增加了 `clear` 子命令，用于一键清空指定文档的全部内容。
- **新增 `replace-markdown` (占位符替换) 命令**：增加了核心功能，可以识别并替换文档中的多个、自定义的占位符（例如 `{{placeholder}}`），并在此位置插入带格式的 Markdown 内容。

### 变更 (Changed)

- **架构升级：客户端/服务器职责分离**：将 `client.py` 重构为支持子命令 (`write`, `clear`, `replace-markdown`) 的智能编排器；将 `mcp_server.py` 重构为纯粹的、包含所有认证和工具调用逻辑的后端服务。
- **架构升级：鉴权模块化**：将所有认证逻辑（服务账号和 OAuth 2.0）从核心工具中剥离，整合到一个独立的 `src/auth.py` 模块中，实现了代码解耦。
- **代码可移植性**：移除了所有脚本和代码中的硬编码绝对路径，通过动态获取相对路径的方式，使整个项目成为一个可被任何人在任何位置下载和使用的、真正的开源项目。

---

## [1.0.0] - 2025-08-21

### 新增 (Added)

- **初始版本发布**：Google Docs Markdown 上传工具首次发布。
- **核心功能**
    - 创建了一个健壮的 Python 工具 (`google_docs_tool.py`)，用于与 Google Docs API 交互。
    - 使用 FastAPI (`mcp_server.py`) 实现了客户端/服务器架构。
- **Markdown 到 Google Docs 的转换引擎**
    - 实现了对多级标题 (`#`, `##`, `###`) 和 **粗体** 文本的支持。
- **专业的项目结构**
    - 将代码库组织成一个专业的 Python 包结构，包含 `src`, `credentials`, `script`, 和 `test` 目录。
    - 创建了 `pyproject.toml` 和 `requirements.txt` 文件来定义项目及其依赖。
    - 实现了 `.gitignore` 文件。
- **全面的测试体系**
    - 开发了本地单元测试和可由环境变量激活的在线集成测试。
    - 创建了主测试运行脚本 (`run_tests.sh`)。
- **项目文档**
    - 创建了 `README.md` 和此 `CHANGELOG.md` 文件。