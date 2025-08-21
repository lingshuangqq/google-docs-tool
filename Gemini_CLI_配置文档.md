# Gemini CLI 配置

Gemini CLI 提供多种方式来配置其行为，包括环境变量、命令行参数和配置文件。本文档概述了不同的配置方法和可用的设置。

## 配置层级

配置按以下优先级顺序应用（序号小的被序号大的覆盖）：

1.  **默认值：** 硬编码在应用程序中的默认值。
2.  **用户配置文件：** 当前用户的全局设置。
3.  **项目配置文件：** 项目特定的设置。
4.  **系统配置文件：** 系统范围的设置。
5.  **环境变量：** 系统范围或会话特定的变量，可能从 `.env` 文件加载。
6.  **命令行参数：** 启动 CLI 时传递的值。

## 配置文件

Gemini CLI 使用 `settings.json` 文件进行持久化配置。这些文件有三个位置：

- **用户配置文件：**
  - **位置：** `~/.gemini/settings.json` (其中 `~` 是您的主目录)。
  - **范围：** 应用于当前用户的所有 Gemini CLI 会话。
- **项目配置文件：**
  - **位置：** 项目根目录下的 `.gemini/settings.json`。
  - **范围：** 仅在从该特定项目运行 Gemini CLI 时应用。项目设置会覆盖用户设置。
- **系统配置文件：**
  - **位置：** `/etc/gemini-cli/settings.json` (Linux)、`C:\ProgramData\gemini-cli\settings.json` (Windows) 或 `/Library/Application Support/GeminiCli/settings.json` (macOS)。该路径可以使用 `GEMINI_CLI_SYSTEM_SETTINGS_PATH` 环境变量覆盖。
  - **范围：** 应用于系统上所有用户的所有 Gemini CLI 会话。系统设置会覆盖用户和项目设置。对于希望控制用户 Gemini CLI 设置的企业系统管理员可能很有用。

**关于配置文件中环境变量的说明：** `settings.json` 文件中的字符串值可以使用 `$VAR_NAME` 或 `${VAR_NAME}` 语法引用环境变量。这些变量在加载设置时会自动解析。例如，如果您有一个环境变量 `MY_API_TOKEN`，您可以在 `settings.json` 中这样使用它：`"apiKey": "$MY_API_TOKEN"`。

### 项目中的 `.gemini` 目录

除了项目配置文件，项目的 `.gemini` 目录还可以包含与 Gemini CLI 操作相关的其他项目特定文件，例如：

- [自定义沙盒配置文件](#sandboxing) (例如, `.gemini/sandbox-macos-custom.sb`, `.gemini/sandbox.Dockerfile`)。

### `settings.json` 中的可用设置：

- **`contextFileName`** (字符串或字符串数组):
  - **描述：** 指定上下文文件的文件名 (例如, `GEMINI.md`, `AGENTS.md`)。可以是一个文件名或接受的文件名列表。
  - **默认值：** `GEMINI.md`
  - **示例：** `"contextFileName": "AGENTS.md"`

- **`bugCommand`** (对象):
  - **描述：** 覆盖 `/bug` 命令的默认 URL。
  - **默认值：** `"urlTemplate": "https://github.com/google-gemini/gemini-cli/issues/new?template=bug_report.yml&title={title}&info={info}"`
  - **属性：**
    - **`urlTemplate`** (字符串): 可以包含 `{title}` 和 `{info}` 占位符的 URL。
  - **示例：**
    ```json
    "bugCommand": {
      "urlTemplate": "https://bug.example.com/new?title={title}&info={info}"
    }
    ```

- **`fileFiltering`** (对象):
  - **描述：** 控制 @ 命令和文件发现工具的 git感知文件过滤行为。
  - **默认值：** `"respectGitIgnore": true, "enableRecursiveFileSearch": true`
  - **属性：**
    - **`respectGitIgnore`** (布尔值): 在发现文件时是否遵循 .gitignore 模式。当设置为 `true` 时，git忽略的文件 (如 `node_modules/`, `dist/`, `.env`) 会自动从 @ 命令和文件列出操作中排除。
    - **`enableRecursiveFileSearch`** (布尔值): 在提示中补全 @ 前缀时，是否在当前树下递归搜索文件名。
  - **示例：**
    ```json
    "fileFiltering": {
      "respectGitIgnore": true,
      "enableRecursiveFileSearch": false
    }
    ```

- **`coreTools`** (字符串数组):
  - **描述：** 允许您指定应提供给模型的核心工具名称列表。这可用于限制内置工具集。有关核心工具列表，请参阅[内置工具](../core/tools-api.md#built-in-tools)。您还可以为支持它的工具指定特定于命令的限制，例如 `ShellTool`。例如，`"coreTools": ["ShellTool(ls -l)"]` 将只允许执行 `ls -l` 命令。
  - **默认值：** 所有工具都可供 Gemini 模型使用。
  - **示例：** `"coreTools": ["ReadFileTool", "GlobTool", "ShellTool(ls)"]`。

- **`excludeTools`** (字符串数组):
  - **描述：** 允许您指定应从模型中排除的核心工具名称列表。同时在 `excludeTools` 和 `coreTools` 中列出的工具将被排除。您还可以为支持它的工具指定特定于命令的限制，例如 `ShellTool`。例如，`"excludeTools": ["ShellTool(rm -rf)"]` 将阻止 `rm -rf` 命令。
  - **默认值**: 不排除任何工具。
  - **示例：** `"excludeTools": ["run_shell_command", "findFiles"]`。
  - **安全说明：** `excludeTools` 中对 `run_shell_command` 的命令特定限制基于简单的字符串匹配，很容易被绕过。此功能**不是安全机制**，不应依赖它来安全地执行不受信任的代码。建议使用 `coreTools` 明确选择可以执行的命令。

- **`allowMCPServers`** (字符串数组):
  - **描述：** 允许您指定应提供给模型的 MCP 服务器名称列表。这可用于限制连接的 MCP 服务器集。请注意，如果设置了 `--allowed-mcp-server-names`，此设置将被忽略。
  - **默认值：** 所有 MCP 服务器都可供 Gemini 模型使用。
  - **示例：** `"allowMCPServers": ["myPythonServer"]`。
  - **安全说明：** 这使用对 MCP 服务器名称的简单字符串匹配，可以被修改。如果您是系统管理员，希望防止用户绕过此设置，请考虑在系统设置级别配置 `mcpServers`，以便用户无法配置自己的任何 MCP 服务器。这不应用作严密的安全机制。

- **`excludeMCPServers`** (字符串数组):
  - **描述：** 允许您指定应从模型中排除的 MCP 服务器名称列表。同时在 `excludeMCPServers` 和 `allowMCPServers` 中列出的服务器将被排除。请注意，如果设置了 `--allowed-mcp-server-names`，此设置将被忽略。
  - **默认值**: 不排除任何 MCP 服务器。
  - **示例：** `"excludeMCPServers": ["myNodeServer"]`。
  - **安全说明：** 这使用对 MCP 服务器名称的简单字符串匹配，可以被修改。如果您是系统管理员，希望防止用户绕过此设置，请考虑在系统设置级别配置 `mcpServers`，以便用户无法配置自己的任何 MCP 服务器。这不应用作严密的安全机制。

- **`autoAccept`** (布尔值):
  - **描述：** 控制 CLI 是否自动接受并执行被认为是安全的工具调用（例如，只读操作），而无需用户明确确认。如果设置为 `true`，CLI 将对被认为是安全的工具绕过确认提示。
  - **默认值：** `false`
  - **示例：** `"autoAccept": true`

- **`theme`** (字符串):
  - **描述：** 设置 Gemini CLI 的视觉[主题](./themes.md)。
  - **默认值：** `"Default"`
  - **示例：** `"theme": "GitHub"`

- **`vimMode`** (布尔值):
  - **描述：** 启用或禁用输入编辑的 vim 模式。启用后，输入区域支持 vim 风格的导航和编辑命令，具有 NORMAL 和 INSERT 模式。vim 模式状态显示在页脚中，并在会话之间保持不变。
  - **默认值：** `false`
  - **示例：** `"vimMode": true`

- **`sandbox`** (布尔值或字符串):
  - **描述：** 控制是否以及如何使用沙盒执行工具。如果设置为 `true`，Gemini CLI 使用预构建的 `gemini-cli-sandbox` Docker 镜像。有关更多信息，请参阅[沙盒](#sandboxing)。
  - **默认值：** `false`
  - **示例：** `"sandbox": "docker"`

- **`toolDiscoveryCommand`** (字符串):
  - **描述：** 定义用于从项目中发现工具的自定义 shell 命令。shell 命令必须在 `stdout` 上返回一个 [函数声明](https://ai.google.dev/gemini-api/docs/function-calling#function-declarations) 的 JSON 数组。工具包装器是可选的。
  - **默认值：** 空
  - **示例：** `"toolDiscoveryCommand": "bin/get_tools"`

- **`toolCallCommand`** (字符串):
  - **描述：** 定义用于调用使用 `toolDiscoveryCommand` 发现的特定工具的自定义 shell 命令。shell 命令必须满足以下条件：
    - 它必须将函数 `name` (与[函数声明](https://ai.google.dev/gemini-api/docs/function-calling#function-declarations)中完全一样) 作为第一个命令行参数。
    - 它必须在 `stdin` 上读取 JSON 格式的函数参数，类似于 [`functionCall.args`](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#functioncall)。
    - 它必须在 `stdout` 上返回 JSON 格式的函数输出，类似于 [`functionResponse.response.content`](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#functionresponse)。
  - **默认值：** 空
  - **示例：** `"toolCallCommand": "bin/call_tool"`

- **`mcpServers`** (对象):
  - **描述：** 配置与一个或多个模型-上下文协议 (MCP) 服务器的连接，以发现和使用自定义工具。Gemini CLI 尝试连接到每个配置的 MCP 服务器以发现可用的工具。如果多个 MCP 服务器公开同名工具，工具名称将以您在配置中定义的服务器别名为前缀 (例如, `serverAlias__actualToolName`) 以避免冲突。请注意，系统可能会从 MCP 工具定义中剥离某些模式属性以确保兼容性。
  - **默认值：** 空
  - **属性：**
    - **`<SERVER_NAME>`** (对象): 命名服务器的服务器参数。
      - `command` (字符串, 必需): 执行以启动 MCP 服务器的命令。
      - `args` (字符串数组, 可选): 传递给命令的参数。
      - `env` (对象, 可选): 为服务器进程设置的环境变量。
      - `cwd` (字符串, 可选): 启动服务器的工作目录。
      - `timeout` (数字, 可选): 对此 MCP 服务器请求的超时时间（毫秒）。
      - `trust` (布尔值, 可选): 信任此服务器并绕过所有工具调用确认。
      - `includeTools` (字符串数组, 可选): 要从此 MCP 服务器包含的工具名称列表。指定后，只有此处列出的工具将从此服务器可用（白名单行为）。如果未指定，则默认启用服务器的所有工具。
      - `excludeTools` (字符串数组, 可选): 要从此 MCP 服务器排除的工具名称列表。此处列出的工具将对模型不可用，即使它们由服务器公开。**注意：** `excludeTools` 优先于 `includeTools` - 如果一个工具同时在两个列表中，它将被排除。
  - **示例：**
    ```json
    "mcpServers": {
      "myPythonServer": {
        "command": "python",
        "args": ["mcp_server.py", "--port", "8080"],
        "cwd": "./mcp_tools/python",
        "timeout": 5000,
        "includeTools": ["safe_tool", "file_reader"],
      },
      "myNodeServer": {
        "command": "node",
        "args": ["mcp_server.js"],
        "cwd": "./mcp_tools/node",
        "excludeTools": ["dangerous_tool", "file_deleter"]
      },
      "myDockerServer": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "-e", "API_KEY", "ghcr.io/foo/bar"],
        "env": {
          "API_KEY": "$MY_API_TOKEN"
        }
      }
    }
    ```

- **`checkpointing`** (对象):
  - **描述：** 配置检查点功能，允许您保存和恢复对话和文件状态。有关更多详细信息，请参阅[检查点文档](../checkpointing.md)。
  - **默认值：** `{"enabled": false}`
  - **属性：**
    - **`enabled`** (布尔值): 当为 `true` 时，`/restore` 命令可用。

- **`preferredEditor`** (字符串):
  - **描述：** 指定用于查看差异的首选编辑器。
  - **默认值：** `vscode`
  - **示例：** `"preferredEditor": "vscode"`

- **`telemetry`** (对象)
  - **描述：** 配置 Gemini CLI 的日志记录和指标收集。有关更多信息，请参阅[遥测](../telemetry.md)。
  - **默认值：** `{"enabled": false, "target": "local", "otlpEndpoint": "http://localhost:4317", "logPrompts": true}`
  - **属性：**
    - **`enabled`** (布尔值): 遥测是否启用。
    - **`target`** (字符串): 收集的遥测数据的目标。支持的值为 `local` 和 `gcp`。
    - **`otlpEndpoint`** (字符串): OTLP 导出器的端点。
    - **`logPrompts`** (布尔值): 是否在日志中包含用户提示的内容。
  - **示例：**
    ```json
    "telemetry": {
      "enabled": true,
      "target": "local",
      "otlpEndpoint": "http://localhost:16686",
      "logPrompts": false
    }
    ```
- **`usageStatisticsEnabled`** (布尔值):
  - **描述：** 启用或禁用使用情况统计信息的收集。有关更多信息，请参阅[使用情况统计](#usage-statistics)。
  - **默认值：** `true`
  - **示例：**
    ```json
    "usageStatisticsEnabled": false
    ```

- **`hideTips`** (布尔值):
  - **描述：** 在 CLI 界面中启用或禁用有用的提示。
  - **默认值：** `false`
  - **示例：**

    ```json
    "hideTips": true
    ```

- **`hideBanner`** (布尔值):
  - **描述：** 在 CLI 界面中启用或禁用启动横幅（ASCII 艺术徽标）。
  - **默认值：** `false`
  - **示例：**

    ```json
    "hideBanner": true
    ```

- **`maxSessionTurns`** (数字):
  - **描述：** 设置会话的最大轮次。如果会话超过此限制，CLI 将停止处理并开始新的聊天。
  - **默认值：** `-1` (无限制)
  - **示例：**
    ```json
    "maxSessionTurns": 10
    ```

- **`summarizeToolOutput`** (对象):
  - **描述：** 启用或禁用工具输出的摘要。您可以使用 `tokenBudget` 设置指定摘要的令牌预算。
  - 注意：目前仅支持 `run_shell_command` 工具。
  - **默认值：** `{}` (默认禁用)
  - **示例：**
    ```json
    "summarizeToolOutput": {
      "run_shell_command": {
        "tokenBudget": 2000
      }
    }
    ```

- **`excludedProjectEnvVars`** (字符串数组):
  - **描述：** 指定应从项目 `.env` 文件加载中排除的环境变量。这可以防止项目特定的环境变量（如 `DEBUG=true`）干扰 gemini-cli 的行为。来自 `.gemini/.env` 文件的变量永远不会被排除。
  - **默认值：** `["DEBUG", "DEBUG_MODE"]`
  - **示例：**
    ```json
    "excludedProjectEnvVars": ["DEBUG", "DEBUG_MODE", "NODE_ENV"]
    ```

- **`includeDirectories`** (字符串数组):
  - **描述：** 指定要包含在工作区上下文中的其他绝对或相对路径的数组。这使您可以像处理单个目录一样处理跨多个目录的文件。路径可以使用 `~` 来引用用户的主目录。此设置可以与 `--include-directories` 命令行标志结合使用。
  - **默认值：** `[]`
  - **示例：**
    ```json
    "includeDirectories": [
      "/path/to/another/project",
      "../shared-library",
      "~/common-utils"
    ]
    ```

- **`loadMemoryFromIncludeDirectories`** (布尔值):
  - **描述：** 控制 `/memory refresh` 命令的行为。如果设置为 `true`，则应从所有添加的目录中加载 `GEMINI.md` 文件。如果设置为 `false`，则 `GEMINI.md` 只应从当前目录加载。
  - **默认值：** `false`
  - **示例：**
    ```json
    "loadMemoryFromIncludeDirectories": true
    ```

- **`chatCompression`** (对象):
  - **描述：** 控制聊天历史压缩的设置，包括自动压缩和通过 /compress 命令手动调用时。
  - **属性：**
    - **`contextPercentageThreshold`** (数字): 一个介于 0 和 1 之间的值，指定压缩的令牌阈值，作为模型总令牌限制的百分比。例如，值 `0.6` 将在聊天历史超过令牌限制的 60% 时触发压缩。
  - **示例：**
    ```json
    "chatCompression": {
      "contextPercentageThreshold": 0.6
    }
    ```

- **`showLineNumbers`** (布尔值):
  - **描述：** 控制是否在 CLI 输出的代码块中显示行号。
  - **默认值：** `true`
  - **示例：**
    ```json
    "showLineNumbers": false
    ```

### `settings.json` 示例：

```json
{
  "theme": "GitHub",
  "sandbox": "docker",
  "toolDiscoveryCommand": "bin/get_tools",
  "toolCallCommand": "bin/call_tool",
  "mcpServers": {
    "mainServer": {
      "command": "bin/mcp_server.py"
    },
    "anotherServer": {
      "command": "node",
      "args": ["mcp_server.js", "--verbose"]
    }
  },
  "telemetry": {
    "enabled": true,
    "target": "local",
    "otlpEndpoint": "http://localhost:4317",
    "logPrompts": true
  },
  "usageStatisticsEnabled": true,
  "hideTips": false,
  "hideBanner": false,
  "maxSessionTurns": 10,
  "summarizeToolOutput": {
    "run_shell_command": {
      "tokenBudget": 100
    }
  },
  "excludedProjectEnvVars": ["DEBUG", "DEBUG_MODE", "NODE_ENV"],
  "includeDirectories": ["path/to/dir1", "~/path/to/dir2", "../path/to/dir3"],
  "loadMemoryFromIncludeDirectories": true
}
```

## Shell 历史

CLI 会记录您运行的 shell 命令的历史。为避免不同项目之间的冲突，此历史记录存储在用户主文件夹内的项目特定目录中。

- **位置：** `~/.gemini/tmp/<project_hash>/shell_history`
  - `<project_hash>` 是根据您的项目根路径生成的唯一标识符。
  - 历史记录存储在名为 `shell_history` 的文件中。

## 环境变量和 `.env` 文件

环境变量是配置应用程序的常用方法，尤其适用于 API 密钥等敏感信息或可能在不同环境之间变化的设置。有关身份验证设置，请参阅[身份验证文档](./authentication.md)，其中涵盖了所有可用的身份验证方法。

CLI 会自动从 `.env` 文件加载环境变量。加载顺序如下：

1.  当前工作目录中的 `.env` 文件。
2.  如果未找到，它会向上搜索父目录，直到找到 `.env` 文件或到达项目根目录（由 `.git` 文件夹标识）或主目录。
3.  如果仍未找到，它会查找 `~/.env`（在用户的主目录中）。

**环境变量排除：** 某些环境变量（如 `DEBUG` 和 `DEBUG_MODE`）会自动从项目 `.env` 文件加载中排除，以防止干扰 gemini-cli 的行为。来自 `.gemini/.env` 文件的变量永远不会被排除。您可以使用 `settings.json` 文件中的 `excludedProjectEnvVars` 设置自定义此行为。

- **`GEMINI_API_KEY`**:
  - 您的 Gemini API 密钥。
  - 多种可用[身份验证方法](./authentication.md)之一。
  - 在您的 shell 配置文件（例如 `~/.bashrc`, `~/.zshrc`）或 `.env` 文件中设置此项。
- **`GEMINI_MODEL`**:
  - 指定要使用的默认 Gemini 模型。
  - 覆盖硬编码的默认值。
  - 示例：`export GEMINI_MODEL="gemini-2.5-flash"`
- **`GOOGLE_API_KEY`**:
  - 您的 Google Cloud API 密钥。
  - 在快速模式下使用 Vertex AI 时需要。
  - 确保您具有必要的权限。
  - 示例：`export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"`。
- **`GOOGLE_CLOUD_PROJECT`**:
  - 您的 Google Cloud 项目 ID。
  - 使用 Code Assist 或 Vertex AI 时需要。
  - 如果使用 Vertex AI，请确保您在此项目中具有必要的权限。
  - **Cloud Shell 注意：** 在 Cloud Shell 环境中运行时，此变量默认为分配给 Cloud Shell 用户的特殊项目。如果您在 Cloud Shell 的全局环境中设置了 `GOOGLE_CLOUD_PROJECT`，它将被此默认值覆盖。要在 Cloud Shell 中使用不同的项目，您必须在 `.env` 文件中定义 `GOOGLE_CLOUD_PROJECT`。
  - 示例：`export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"`。
- **`GOOGLE_APPLICATION_CREDENTIALS`** (字符串):
  - **描述：** 您的 Google Application Credentials JSON 文件的路径。
  - **示例：** `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"`
- **`OTLP_GOOGLE_CLOUD_PROJECT`**:
  - 您用于 Google Cloud 中遥测的 Google Cloud 项目 ID。
  - 示例：`export OTLP_GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"`。
- **`GOOGLE_CLOUD_LOCATION`**:
  - 您的 Google Cloud 项目位置（例如 us-central1）。
  - 在非快速模式下使用 Vertex AI 时需要。
  - 示例：`export GOOGLE_CLOUD_LOCATION="YOUR_PROJECT_LOCATION"`。
- **`GEMINI_SANDBOX`**:
  - `settings.json` 中 `sandbox` 设置的替代方案。
  - 接受 `true`、`false`、`docker`、`podman` 或自定义命令字符串。
- **`SEATBELT_PROFILE`** (macOS 特定):
  - 在 macOS 上切换 Seatbelt (`sandbox-exec`) 配置文件。
  - `permissive-open`: (默认) 限制对项目文件夹（以及其他一些文件夹，请参阅 `packages/cli/src/utils/sandbox-macos-permissive-open.sb`）的写入，但允许其他操作。
  - `strict`: 使用默认拒绝操作的严格配置文件。
  - `<profile_name>`: 使用自定义配置文件。要定义自定义配置文件，请在项目的 `.gemini/` 目录中创建一个名为 `sandbox-macos-<profile_name>.sb` 的文件（例如 `my-project/.gemini/sandbox-macos-custom.sb`）。
- **`DEBUG` 或 `DEBUG_MODE`** (通常由底层库或 CLI 本身使用):
  - 设置为 `true` 或 `1` 以启用详细的调试日志记录，这有助于故障排除。
  - **注意：** 默认情况下，这些变量会自动从项目 `.env` 文件中排除，以防止干扰 gemini-cli 的行为。如果您需要为 gemini-cli 特别设置这些变量，请使用 `.gemini/.env` 文件。
- **`NO_COLOR`**:
  - 设置为任何值以禁用 CLI 中的所有颜色输出。
- **`CLI_TITLE`**:
  - 设置为字符串以自定义 CLI 的标题。
- **`CODE_ASSIST_ENDPOINT`**:
  - 指定代码辅助服务器的端点。
  - 这对于开发和测试很有用。

## 命令行参数

在运行 CLI 时直接传递的参数可以覆盖该特定会话的其他配置。

- **`--model <model_name>`** (**`-m <model_name>`**):
  - 指定此会话要使用的 Gemini 模型。
  - 示例：`npm start -- --model gemini-1.5-pro-latest`
- **`--prompt <your_prompt>`** (**`-p <your_prompt>`**):
  - 用于将提示直接传递给命令。这会以非交互模式调用 Gemini CLI。
- **`--prompt-interactive <your_prompt>`** (**`-i <your_prompt>`**):
  - 使用提供的提示作为初始输入启动交互式会话。
  - 提示在交互式会话中处理，而不是在会话开始前。
  - 不能与从 stdin 管道输入一起使用。
  - 示例：`gemini -i "explain this code"`
- **`--sandbox`** (**`-s`**):
  - 为此会话启用沙盒模式。
- **`--sandbox-image`**:
  - 设置沙盒镜像 URI。
- **`--debug`** (**`-d`**):
  - 为此会话启用调试模式，提供更详细的输出。
- **`--all-files`** (**`-a`**):
  - 如果设置，则递归地将当前目录中的所有文件作为提示的上下文。
- **`--help`** (或 **`-h`**):
  - 显示有关命令行参数的帮助信息。
- **`--show-memory-usage`**:
  - 显示当前内存使用情况。
- **`--yolo`**:
  - 启用 YOLO 模式，该模式会自动批准所有工具调用。
- **`--approval-mode <mode>`**:
  - 设置工具调用的批准模式。可用模式：
    - `default`: 对每个工具调用提示批准（默认行为）
    - `auto_edit`: 自动批准编辑工具（replace, write_file），同时提示其他工具
    - `yolo`: 自动批准所有工具调用（相当于 `--yolo`）
  - 不能与 `--yolo` 一起使用。使用 `--approval-mode=yolo` 代替 `--yolo` 以实现新的统一方法。
  - 示例：`gemini --approval-mode auto_edit`
- **`--telemetry`**:
  - 启用[遥测](../telemetry.md)。
- **`--telemetry-target`**:
  - 设置遥测目标。有关更多信息，请参阅[遥测](../telemetry.md)。
- **`--telemetry-otlp-endpoint`**:
  - 设置遥测的 OTLP 端点。有关更多信息，请参阅[遥测](../telemetry.md)。
- **`--telemetry-otlp-protocol`**:
  - 设置遥测的 OTLP 协议（`grpc` 或 `http`）。默认为 `grpc`。有关更多信息，请参阅[遥测](../telemetry.md)。
- **`--telemetry-log-prompts`**:
  - 启用遥测的提示日志记录。有关更多信息，请参阅[遥测](../telemetry.md)。
- **`--checkpointing`**:
  - 启用[检查点](../checkpointing.md)。
- **`--extensions <extension_name ...>`** (**`-e <extension_name ...>`**):
  - 指定会话要使用的扩展列表。如果未提供，则使用所有可用的扩展。
  - 使用特殊术语 `gemini -e none` 禁用所有扩展。
  - 示例：`gemini -e my-extension -e my-other-extension`
- **`--list-extensions`** (**`-l`**):
  - 列出所有可用的扩展并退出。
- **`--proxy`**:
  - 设置 CLI 的代理。
  - 示例：`--proxy http://localhost:7890`。
- **`--include-directories <dir1,dir2,...>`**:
  - 在工作区中包含其他目录以支持多目录。
  - 可以多次指定或以逗号分隔的值指定。
  - 最多可以添加 5 个目录。
  - 示例：`--include-directories /path/to/project1,/path/to/project2` 或 `--include-directories /path/to/project1 --include-directories /path/to/project2`
- **`--version`**:
  - 显示 CLI 的版本。

## 上下文文件（分层指令上下文）

虽然上下文文件（默认为 `GEMINI.md`，但可通过 `contextFileName` 设置配置）不严格算是 CLI *行为*的配置，但它们对于配置提供给 Gemini 模型的*指令上下文*（也称为“记忆”）至关重要。这个强大的功能允许您提供项目特定的指令、编码风格指南或任何相关的背景信息给 AI，使其响应更贴合您的需求和项目。CLI 包含 UI 元素，例如页脚中显示已加载上下文文件数量的指示器，让您随时了解活动的上下文。

- **目的：** 这些 Markdown 文件包含您希望 Gemini 模型在交互过程中了解的指令、指南或上下文。系统旨在分层管理此指令上下文。

### 上下文文件内容示例 (例如, `GEMINI.md`)

这是一个 TypeScript 项目根目录下的上下文文件可能包含的内容的概念性示例：

```markdown
# 项目：我的超棒 TypeScript 库

## 通用指令：

- 生成新的 TypeScript 代码时，请遵循现有的编码风格。
- 确保所有新函数和类都有 JSDoc 注释。
- 在适当的情况下，优先使用函数式编程范式。
- 所有代码都应与 TypeScript 5.0 和 Node.js 20+ 兼容。

## 编码风格：

- 使用 2 个空格进行缩进。
- 接口名称应以 `I` 为前缀 (例如, `IUserService`)。
- 私有类成员应以下划线 (`_`) 为前缀。
- 始终使用严格相等 (`===` 和 `!==`)。

## 特定组件：`src/api/client.ts`

- 此文件处理所有出站 API 请求。
- 添加新的 API 调用函数时，请确保它们包含健壮的错误处理和日志记录。
- 对所有 GET 请求使用现有的 `fetchWithRetry` 实用程序。

## 关于依赖项：

- 除非绝对必要，否则避免引入新的外部依赖项。
- 如果需要新的依赖项，请说明原因。
```

此示例演示了如何提供通用的项目上下文、特定的编码约定，甚至有关特定文件或组件的注释。您的上下文文件越相关、越精确，AI 就能更好地帮助您。强烈建议使用项目特定的上下文文件来建立约定和上下文。

- **分层加载和优先级：** CLI 通过从多个位置加载上下文文件（例如 `GEMINI.md`）来实现一个复杂的分层记忆系统。列表中位置较低（更具体）的文件内容通常会覆盖或补充位置较高（更通用）的文件内容。确切的连接顺序和最终上下文可以使用 `/memory show` 命令进行检查。典型的加载顺序是：
  1.  **全局上下文文件：**
      - 位置：`~/.gemini/<contextFileName>` (例如, 用户主目录中的 `~/.gemini/GEMINI.md`)。
      - 范围：为您所有的项目提供默认指令。
  2.  **项目根目录和祖先目录上下文文件：**
      - 位置：CLI 在当前工作目录中搜索配置的上下文文件，然后在每个父目录中向上搜索，直到项目根目录（由 `.git` 文件夹标识）或您的主目录。
      - 范围：提供与整个项目或其重要部分相关的上下文。
  3.  **子目录上下文文件（上下文/本地）：**
      - 位置：CLI 还会扫描当前工作目录*下方*的子目录以查找配置的上下文文件（遵循常见的忽略模式，如 `node_modules`、`.git` 等）。默认情况下，此搜索的广度限制为 200 个目录，但可以在 `settings.json` 文件中使用 `memoryDiscoveryMaxDirs` 字段进行配置。
      - 范围：允许针对项目的特定组件、模块或子部分提供高度具体的指令。
- **连接和 UI 指示：** 所有找到的上下文文件的内容都会被连接起来（并带有指示其来源和路径的分隔符），并作为系统提示的一部分提供给 Gemini 模型。CLI 页脚会显示已加载的上下文文件数量，为您提供有关活动指令上下文的快速视觉提示。
- **导入内容：** 您可以使用 ` @path/to/file.md` 语法导入其他 Markdown 文件来模块化您的上下文文件。有关更多详细信息，请参阅[记忆导入处理器文档](../core/memport.md)。
- **内存管理命令：**
  - 使用 `/memory refresh` 强制从所有配置的位置重新扫描和重新加载所有上下文文件。这将更新 AI 的指令上下文。
  - 使用 `/memory show` 显示当前加载的组合指令上下文，让您验证 AI 正在使用的层次结构和内容。
  - 有关 `/memory` 命令及其子命令（`show` 和 `refresh`）的完整详细信息，请参阅[命令文档](./commands.md#memory)。

通过理解和利用这些配置层级以及上下文文件的分层特性，您可以有效地管理 AI 的记忆，并根据您的特定需求和项目定制 Gemini CLI 的响应。

## 沙盒

Gemini CLI 可以在沙盒环境中执行潜在不安全的操作（如 shell 命令和文件修改），以保护您的系统。

沙盒默认禁用，但您可以通过几种方式启用它：

- 使用 `--sandbox` 或 `-s` 标志。
- 设置 `GEMINI_SANDBOX` 环境变量。
- 默认情况下，在使用 `--yolo` 或 `--approval-mode=yolo` 时启用沙盒。

默认情况下，它使用预构建的 `gemini-cli-sandbox` Docker 镜像。

对于项目特定的沙盒需求，您可以在项目根目录的 `.gemini/sandbox.Dockerfile` 创建一个自定义 Dockerfile。此 Dockerfile 可以基于基础沙盒镜像：

```dockerfile
FROM gemini-cli-sandbox

# 在此处添加您的自定义依赖项或配置
# 例如：
# RUN apt-get update && apt-get install -y some-package
# COPY ./my-config /app/my-config
```

当 `.gemini/sandbox.Dockerfile` 存在时，您可以在运行 Gemini CLI 时使用 `BUILD_SANDBOX` 环境变量来自动构建自定义沙盒镜像：

```bash
BUILD_SANDBOX=1 gemini -s
```

## 使用情况统计

为了帮助我们改进 Gemini CLI，我们收集匿名的使用情况统计信息。这些数据有助于我们了解 CLI 的使用方式，识别常见问题，并确定新功能的优先级。

**我们收集什么：**

- **工具调用：** 我们记录被调用的工具的名称，它们是成功还是失败，以及执行所需的时间。我们不收集传递给工具的参数或工具返回的任何数据。
- **API 请求：** 我们记录每个请求使用的 Gemini 模型、请求的持续时间以及是否成功。我们不收集提示或响应的内容。
- **会话信息：** 我们收集有关 CLI 配置的信息，例如启用的工具和批准模式。

**我们不收集什么：**

- **个人身份信息 (PII)：** 我们不收集任何个人信息，例如您的姓名、电子邮件地址或 API 密钥。
- **提示和响应内容：** 我们不记录您的提示内容或 Gemini 模型的响应。
- **文件内容：** 我们不记录 CLI 读取或写入的任何文件的内容。

**如何选择退出：**

您可以随时通过在 `settings.json` 文件中将 `usageStatisticsEnabled` 属性设置为 `false` 来选择退出使用情况统计信息的收集：

```json
{
  "usageStatisticsEnabled": false
}
```
