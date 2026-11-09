> ## Documentation Index
> Fetch the complete documentation index at: https://docs.ollama.com/llms.txt
> Use this file to discover all available pages before exploring further.

# OpenCode

[OpenCode](https://opencode.ai) is an open-source coding agent that runs in your terminal, reads your project, edits files, and runs commands.

Ollama configures OpenCode to use local and cloud models.

## Get started

Launch OpenCode with Ollama:

```shell theme={"system"}
ollama launch opencode
```

## Capabilities

ChatAsk questions about a repository or task

Command lineRun commands from your working directory

File editsRead and edit files in your project

SubagentsSplit work across tasks

Web fetchFetch and summarize web pages

VisionSend images and screenshots

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
> OpenCode requires a context length of 64k or higher. See [Context length](https://docs.ollama.com/context-length.md) for more information.

## Manual setup

1\. Install OpenCode

```shell macOS / Linux theme={"system"}
curl -fsSL https://opencode.ai/install | bash
```

```powershell Windows theme={"system"}
npm install -g opencode-ai
```

2\. Configure Ollama as a provider

Add an Ollama provider to `opencode.json`:

```json theme={"system"}
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen3.5": {
          "name": "qwen3.5"
        }
      }
    }
  }
}
```

3\. Run OpenCode

```shell theme={"system"}
opencode
```

To configure OpenCode with Ollama without starting an interactive session:

```shell theme={"system"}
ollama launch opencode --config
```

### Configuration precedence

`ollama launch opencode` starts OpenCode with an inline config for the selected Ollama model. It does not overwrite `~/.config/opencode/opencode.json`; existing OpenCode settings still apply.

Models defined only in `opencode.json` do not appear in the `ollama launch` model picker.

See OpenCode's [config precedence](https://opencode.ai/docs/config/#precedence-order).
