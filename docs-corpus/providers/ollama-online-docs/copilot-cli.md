> ## Documentation Index
> Fetch the complete documentation index at: https://docs.ollama.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Copilot CLI

GitHub Copilot CLI is GitHub's AI coding agent for the terminal. It can understand your codebase, make edits, run commands, and help you build software faster.

Open models can be used with Copilot CLI through Ollama, enabling you to use models such as `qwen3.5`, `glm-5.3:cloud`, `kimi-k3:cloud` See all supported models [here](https://ollama.com/search).

## Install

Install [Copilot CLI](https://github.com/features/copilot/cli/):

```shell macOS / Linux (Homebrew) theme={"system"}
brew install copilot-cli
```

```shell npm (all platforms) theme={"system"}
npm install -g @github/copilot
```

```shell macOS / Linux (script) theme={"system"}
curl -fsSL https://gh.io/copilot-install | bash
```

```powershell Windows (WinGet) theme={"system"}
winget install GitHub.Copilot
```

## Usage with Ollama

### Quick setup

```shell theme={"system"}
ollama launch copilot
```

### Run directly with a model

```shell theme={"system"}
ollama launch copilot --model kimi-k2.5:cloud
```

## Non-interactive (headless) mode

Run Copilot CLI without interaction for use in Docker, CI/CD, or scripts:

```shell theme={"system"}
ollama launch copilot --model kimi-k2.5:cloud --yes -- -p "how does this repository work?"
```

The `--yes` flag auto-pulls the model, skips selectors, and requires `--model` to be specified. Arguments after `--` are passed directly to Copilot CLI.

## Manual setup

Copilot CLI connects to Ollama using the OpenAI-compatible API via environment variables.

1. Set the environment variables:

```shell theme={"system"}
export COPILOT_PROVIDER_BASE_URL=http://localhost:11434/v1
export COPILOT_PROVIDER_API_KEY=
export COPILOT_PROVIDER_WIRE_API=responses
export COPILOT_MODEL=qwen3.5
```

1. Run Copilot CLI:

```shell theme={"system"}
copilot
```

Or run with environment variables inline:

```shell theme={"system"}
COPILOT_PROVIDER_BASE_URL=http://localhost:11434/v1 COPILOT_PROVIDER_API_KEY= COPILOT_PROVIDER_WIRE_API=responses COPILOT_MODEL=glm-5:cloud copilot
```

**Note:** Copilot requires a large context window. We recommend at least 64k tokens. See the [context length documentation](https://docs.ollama.com/context-length.md) for how to adjust context length in Ollama.
