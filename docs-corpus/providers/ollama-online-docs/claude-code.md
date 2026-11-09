> ## Documentation Index
> Fetch the complete documentation index at: https://docs.ollama.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude Code

[Claude Code](https://code.claude.com/docs/en/overview) reads your codebase, edits files, and runs commands.

Ollama connects Claude Code to local and cloud models through its Anthropic-compatible API.

## Get started

Launch Claude Code with Ollama:

```shell theme={"system"}
ollama launch claude
```

## Capabilities

ChatAsk questions about a repository or task

Command lineRun commands with Claude Code's permission flow

Tool callingUse tools with compatible models

File editsRead and edit files in your project

SubagentsSplit work across tasks

Web searchSearch the web through Ollama

Web fetchFetch and summarize web pages

VisionSend images and screenshots

ThinkingUse thinking controls with compatible models

## Models

Choose a model with enough context for your repository.

> [card] [Cloud models](https://ollama.com/search?c=cloud)
>
> Use larger models without downloading them.

> [card] [Local models](https://ollama.com/search?c=tools)
>
> Choose a model and set a 64k+ context window.

> [!NOTE]
>
> For larger repositories, set the [context length](https://docs.ollama.com/context-length.md) to 64k or higher.

## More features

### Run without interaction

Use `--yes` for scripts, Docker, or CI:

```shell theme={"system"}
ollama launch claude --model gemma4:cloud --yes -- -p "how does this repository work?"
```

The `--yes` flag skips selectors, pulls the model when needed, and requires `--model`. Arguments after `--` are passed directly to Claude Code.

### Web search

Use Ollama's web search API from Claude Code.

See [Web search](https://docs.ollama.com/capabilities/web-search.md) for setup and usage.

### Scheduled tasks with `/loop`

Use `/loop` inside Claude Code to run a prompt or slash command on a schedule:

```text theme={"system"}
/loop <interval> <prompt or /command>
```

Examples:

```text theme={"system"}
/loop 30m Check my open PRs and summarize their status
/loop 1h Research the latest AI news and summarize key developments
/loop 15m Check for new GitHub issues and triage by priority
```

### Telegram

Connect a Telegram bot to your Claude Code session. Install the [Telegram plugin](https://github.com/anthropics/claude-plugins-official), create a bot with [@BotFather](https://t.me/BotFather), then launch Claude Code:

```shell theme={"system"}
ollama launch claude -- --channels plugin:telegram@claude-plugins-official
```

Claude Code prompts for permission on most actions. To allow the bot to work autonomously, configure [permission rules](https://code.claude.com/docs/en/permissions) or pass `--dangerously-skip-permissions` in an isolated environment.

See the [plugin README](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram) for setup instructions.

## Connect directly to Ollama's cloud

Install Claude Code, then set your [API key](https://docs.ollama.com/quickstart.md#build-an-application) in `OLLAMA_API_KEY`. No Ollama installation required.

In Bash or Zsh, run:

```shell theme={"system"}
ANTHROPIC_BASE_URL=https://ollama.com \
ANTHROPIC_AUTH_TOKEN="$OLLAMA_API_KEY" \
ANTHROPIC_API_KEY="" \
claude --model glm-5.3-flash
```

Use `ANTHROPIC_AUTH_TOKEN` for bearer authentication. Claude settings can override shell variables. Update any base URL or credentials in those settings, then run `/status` to check the connection.

Choose a [cloud model](https://ollama.com/search?c=cloud) that supports tools. Basic chat and file edits work with compatible models. Hosted WebSearch and advanced tool controls are not fully supported. See [Anthropic compatibility](https://docs.ollama.com/api/anthropic-compatibility.md).

## Manual setup

1\. Install Claude Code

```shell macOS / Linux theme={"system"}
curl -fsSL https://claude.ai/install.sh | bash
```

```powershell Windows theme={"system"}
irm https://claude.ai/install.ps1 | iex
```

2\. Set the environment variables

```shell theme={"system"}
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_API_KEY=""
export ANTHROPIC_BASE_URL=http://localhost:11434
```

3\. Run Claude Code

```shell theme={"system"}
claude --model qwen3.5
```

Or run with environment variables inline:

```shell theme={"system"}
ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_API_KEY="" claude --model kimi-k2.7-code:cloud
```
