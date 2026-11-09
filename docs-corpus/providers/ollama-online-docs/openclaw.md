> ## Documentation Index
> Fetch the complete documentation index at: https://docs.ollama.com/llms.txt
> Use this file to discover all available pages before exploring further.

# OpenClaw

OpenClaw is a personal AI assistant that runs on your own devices. It bridges messaging services (WhatsApp, Telegram, Slack, Discord, iMessage, and more) to AI coding agents through a centralized gateway.

## Quick start

```bash theme={"system"}
ollama launch openclaw
```

Ollama handles everything automatically:

1. **Install** — If OpenClaw isn't installed, Ollama prompts to install it via npm
2. **Security** — On the first launch, a security notice explains the risks of tool access
3. **Model** — Pick a model from the selector (see supported local and cloud models [here](https://ollama.com/search))
4. **Onboarding** — Ollama configures the provider, installs the gateway daemon, sets your model as the primary, and enables OpenClaw's bundled Ollama web search
5. **Gateway** — Starts in the background and opens the OpenClaw TUI

> [!NOTE]
>
> OpenClaw requires a larger context window. It is recommended to use a context window of at least 64k tokens if using local models. See [Context length](https://docs.ollama.com/context-length.md) for more information.

> [!NOTE]
>
> Previously known as Clawdbot. `ollama launch clawdbot` still works as an alias.

## Web search and fetch

OpenClaw ships with a bundled Ollama `web_search` provider that lets local or cloud-backed Ollama setups search the web through the configured Ollama host.

```bash theme={"system"}
ollama launch openclaw
```

Ollama web search is enabled automatically when launching OpenClaw through Ollama. To configure it manually:

```bash theme={"system"}
openclaw configure --section web
```

> [!NOTE]
>
> Ollama web search for local models requires `ollama signin`.

## Configure without launching

To change the model without starting the gateway and TUI:

```bash theme={"system"}
ollama launch openclaw --config
```

To use a specific model directly:

```bash theme={"system"}
ollama launch openclaw --model kimi-k2.5:cloud
```

If the gateway is already running, it restarts automatically to pick up the new model.

## Non-interactive (headless) mode

Run OpenClaw without interaction for use in Docker, CI/CD, or scripts:

```bash theme={"system"}
ollama launch openclaw --model kimi-k2.5:cloud --yes
```

The `--yes` flag auto-pulls the model, skips selectors, and requires `--model` to be specified.

## Connect messaging apps

```bash theme={"system"}
openclaw configure --section channels
```

Link WhatsApp, Telegram, Slack, Discord, or iMessage to chat with your local models from anywhere.

## Stopping the gateway

```bash theme={"system"}
openclaw gateway stop
```
