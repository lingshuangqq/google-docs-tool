# Google Docs Markdown Uploader

这是一个功能强大的命令行工具集，允许用户将本地的 Markdown 文件（支持标题、粗体、多级列表等）写入指定的 Google 文档中。本项目采用客户端/服务器架构，支持服务账号和用户 OAuth 2.0 两种鉴权模式，并可通过占位符模式，在文档的任意位置插入内容。

## 架构图

![项目架构图](./gmp_module_architecture_en.png)

---

## 1. 环境准备 (Prerequisites)

- **Python 3.10+**
- **uv**: 一个现代的 Python 包管理器。如果尚未安装，请运行 `pip3 install uv`。

## 2. 配置步骤 (Setup)

根据您希望使用的鉴权模式，您需要从 Google Cloud Console 获取相应的凭证。

### 步骤 2.1: 获取凭证

**选项A：服务账号模式 (适用于自动化、后台任务)**
1.  在 [Google Cloud Console](https://console.cloud.google.com/) 的 **IAM 与管理** > **服务账号** 页面创建一个服务账号。
2.  授予它**编辑者 (Editor)** 角色。
3.  为该服务账号创建一个 **JSON 格式** 的密钥，并下载它。
4.  将下载的密钥文件放入本项目的 `credentials/` 目录下（例如，命名为 `docs-writer-credentials.json`）。

**选项B：OAuth 2.0 模式 (适用于让普通用户以自己的身份操作)**
1.  在 [Google Cloud Console 的凭证页面](https://console.cloud.google.com/apis/credentials) 点击 **+ 创建凭证** > **OAuth 客户端 ID**。
2.  应用类型选择 **桌面应用 (Desktop app)**。
3.  创建后，**下载 JSON** 文件。
4.  将下载的客户端密钥文件放入本项目的 `credentials/` 目录下（例如，命名为 `oauth-credentials.json`）。
5.  **重要**: 在GCP控制台的 OAuth 同意屏幕设置中，确保将您的 Google 账户添加为测试用户。

### 步骤 2.2: 为 Google 文档授权

1.  打开您希望本工具操作的目标 Google 文档。
2.  点击右上角的 **共享 (Share)** 按钮。
3.  将您的**服务账号的电子邮件地址**（来自服务账号JSON文件）或您**自己的Google账户邮箱**（如果您使用OAuth模式）添加为**编辑者 (Editor)**。

### 步骤 2.3: 安装项目依赖

1.  在终端中，进入本项目根目录 (`google-docs-tool`)。
2.  使用 `uv` 创建并激活虚拟环境：
    ```bash
    uv venv
    source .venv/bin/activate
    ```
3.  安装所有依赖：
    ```bash
    uv pip install -r requirements.txt
    ```

## 3. 使用指南 (Usage)

本工具采用客户端/服务器模式，您需要先启动服务，再运行客户端。

### 步骤 3.1: 启动服务

- 在一个终端窗口中，确保您位于项目根目录 (`google-docs-tool`) 下，并已激活虚拟环境。
- 使用 `-m` 方式启动服务，并使其保持运行：
  ```bash
  python3 -m src.server.mcp_server
  ```

### 步骤 3.2: 运行客户端

- 打开**另一个**终端窗口，同样进入项目根目录 (`google-docs-tool`)。
- 使用 `src/client.py` 脚本，并指定一个子命令 (`write`, `clear`, `replace-markdown`)。

**示例 1: 【写入】一个全新的文档 (使用OAuth模式)**
```bash
python3 src/client.py write ../path/to/your/report.md --title "我的新报告" --auth oauth --creds-path ./credentials/oauth-credentials.json
```

**示例 2: 【清空】一个已存在的文档 (使用服务账号模式)**
```bash
python3 src/client.py clear "你的文档ID" --auth service_account --creds-path ./credentials/docs-writer-credentials.json
```

**示例 3: 【替换】文档中的占位符 (使用OAuth模式)**
```bash
# 假设文档中已有 {{MY_PLACEHOLDER}}
python3 src/client.py replace-markdown "你的文档ID" --replace "{{MY_PLACEHOLDER}}" ../path/to/your/content.md --auth oauth --creds-path ./credentials/oauth-credentials.json
```

## 4. 测试指南 (Testing)

所有测试命令都应在项目根目录 (`google-docs-tool`) 下运行。

```bash
# 运行快速的本地单元测试
./run_tests.sh

# 运行需要真实API和凭证的在线集成测试
./run_tests.sh --online --doc-id "你的文档ID" --creds-path "./credentials/oauth-credentials.json"
```