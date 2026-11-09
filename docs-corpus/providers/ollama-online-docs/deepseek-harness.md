> ## Documentation Index
> Fetch the complete documentation index at: https://docs.ollama.com/llms.txt
> Use this file to discover all available pages before exploring further.

# DeepSeek Harness

[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) is an open-source coding agent.

> [!NOTE]
>
> DeepSeek Harness is currently a developer preview. Its upstream configuration may change between releases.

## Setup

```shell theme={"system"}
ollama launch dsh
```

Ollama installs `@deepseek-ai/dsh` if needed. To choose a model:

```shell theme={"system"}
ollama launch dsh --model qwen3.8
ollama launch dsh --model deepseek-v4-flash:cloud
```

To configure without starting:

```shell theme={"system"}
ollama launch dsh --config
```

## Web search

Web search is enabled automatically. It requires access to Ollama's cloud and a model that supports tools. Run `ollama signin` if needed.

## Configuration

Ollama stores its settings in `~/.ollama/launch/dsh/settings.yaml`. These settings load last and set the model, provider, and web search connection. Repeated launches preserve other settings in this file. Ollama does not change `~/.dsh/settings.yaml`, profiles, sessions, or credentials.

Launch rejects additional `--patch` arguments. Pass other Harness arguments after `--`:

```shell theme={"system"}
ollama launch dsh -- --port 3081
```

## Manual install

DeepSeek Harness requires Node.js. To install it manually:

```shell theme={"system"}
npm install -g @deepseek-ai/dsh@latest
```

Then run `ollama launch dsh`. On Windows, install Node.js for Windows.
