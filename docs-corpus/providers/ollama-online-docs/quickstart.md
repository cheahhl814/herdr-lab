> ## Documentation Index
> Fetch the complete documentation index at: https://docs.ollama.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Quickstart

Use Ollama in [desktop apps](#connect-a-desktop-app) and [coding agents](#use-a-coding-agent), or [build an application](#build-an-application) with an API key.

## Get started

[Download Ollama](https://ollama.com/download) for macOS, Windows, or Linux. Open the app, or get started from your terminal:

```shell theme={"system"}
ollama
```

Follow the setup prompts. Sign in to use cloud models, or choose a local model.

## Connect a desktop app

On macOS, open Ollama and select **Apps**. Connect **Claude** or **ChatGPT (Desktop)**. Follow the prompts to install or restart the app.

Choose your Ollama models in **Settings → Apps**.

* [Claude Desktop](https://docs.ollama.com/integrations/claude-desktop.md) — use Ollama models in Claude.
* [ChatGPT Desktop](https://docs.ollama.com/integrations/chatgpt.md) — use Ollama models in Codex mode. Regular Chat and voice use your usual ChatGPT connection.

## Use a coding agent

From your project directory, launch your agent:

> [tab] Claude Code
>
> ```shell theme={"system"}
> ollama launch claude
> ```
>
> Ollama offers to install Claude Code if needed. See [Claude Code](https://docs.ollama.com/integrations/claude-code.md) for details.

> [tab] Codex CLI
>
> [Install Codex CLI](https://docs.ollama.com/integrations/codex.md#install) first, then launch it:
>
> ```shell theme={"system"}
> ollama launch codex
> ```
>
> See [Codex CLI](https://docs.ollama.com/integrations/codex.md) for setup.

> [tab] OpenCode
>
> ```shell theme={"system"}
> ollama launch opencode
> ```
>
> Ollama offers to install OpenCode if needed. See [OpenCode](https://docs.ollama.com/integrations/opencode.md) for details.

Choose a model when prompted, then try:

```text theme={"system"}
Explain how this repository is organized.
```

For more tools, see [Integrations](https://docs.ollama.com/integrations.md). To connect an agent directly with an API key, see [Claude Code](https://docs.ollama.com/integrations/claude-code.md#connect-directly-to-ollama-cloud).

## Build an application

Use cloud models with an API key, or run models locally without one. Cloud requests do not require an Ollama installation.

### 1. Create an API key

For local models, skip this step and select **Local** under [Send a request](#2-send-a-request).

For cloud models, sign in or create an account, then create an [API key](https://ollama.com/settings/keys).

Set your key in the terminal:

```shell macOS / Linux theme={"system"}
export OLLAMA_API_KEY="your_api_key"
```

```powershell Windows theme={"system"}
$env:OLLAMA_API_KEY = "your_api_key"
```

Keep your key on your application's server, outside browser code and source control.

### 2. Send a request

Make your first request to Ollama

> [tab] Cloud
>
> These examples use the `gemma4:31b` [cloud model](https://ollama.com/search?c=cloud).
>
> > [tab] Ollama API
> >
> > ```shell theme={"system"}
> > curl https://ollama.com/api/chat \
> >   -H "Authorization: Bearer $OLLAMA_API_KEY" \
> >   -H "Content-Type: application/json" \
> >   -d '{
> >     "model": "gemma4:31b",
> >     "messages": [
> >       {
> >         "role": "user",
> >         "content": "Say hello in one sentence."
> >       }
> >     ],
> >     "stream": false
> >   }'
> > ```
> >
> > Read the answer from `message.content`. See [Ollama's API and libraries](https://docs.ollama.com/api/introduction.md).
>
> > [tab] OpenAI Chat Completions
> >
> > ```shell theme={"system"}
> > curl https://ollama.com/v1/chat/completions \
> >   -H "Authorization: Bearer $OLLAMA_API_KEY" \
> >   -H "Content-Type: application/json" \
> >   -d '{
> >     "model": "gemma4:31b",
> >     "messages": [
> >       {
> >         "role": "user",
> >         "content": "Say hello in one sentence."
> >       }
> >     ]
> >   }'
> > ```
> >
> > Read the answer from `choices[0].message.content`. See [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility.md) for client setup and supported features.
>
> > [tab] OpenAI Responses
> >
> > ```shell theme={"system"}
> > curl https://ollama.com/v1/responses \
> >   -H "Authorization: Bearer $OLLAMA_API_KEY" \
> >   -H "Content-Type: application/json" \
> >   -d '{
> >     "model": "gemma4:31b",
> >     "input": "Say hello in one sentence."
> >   }'
> > ```
> >
> > Read the `output_text` content blocks inside `output`. The OpenAI Python client exposes the text as `response.output_text`.
> >
> > Responses requests are stateless: include conversation history in each request. `previous_response_id` and `conversation` aren't supported. See [Responses compatibility](https://docs.ollama.com/api/openai-compatibility.md#responses-api).
>
> > [tab] Anthropic Messages
> >
> > ```shell theme={"system"}
> > curl https://ollama.com/v1/messages \
> >   -H "Authorization: Bearer $OLLAMA_API_KEY" \
> >   -H "Content-Type: application/json" \
> >   -H "anthropic-version: 2023-06-01" \
> >   -d '{
> >     "model": "gemma4:31b",
> >     "max_tokens": 1024,
> >     "messages": [
> >       {
> >         "role": "user",
> >         "content": "Say hello in one sentence."
> >       }
> >     ]
> >   }'
> > ```
> >
> > Read text blocks from `content`. Direct cloud requests use bearer authentication. See [Anthropic compatibility](https://docs.ollama.com/api/anthropic-compatibility.md) for client setup and supported features.
>
> OpenAI and Anthropic compatibility each cover a subset of the original API. See [Cloud](https://docs.ollama.com/cloud.md) for models and usage limits.

> [tab] Local
>
> Run [Gemma 4 E2B](https://ollama.com/library/gemma4:e2b) on your computer. No API key required.
>
> > [!NOTE]
> >
> > The model download is about 7.2 GB. We recommend 8 GB of available VRAM, or unified memory on a Mac. Larger context windows need more memory. With less VRAM, Ollama can use system RAM, but responses may be slower.
>
> [Download Ollama](https://ollama.com/download) and open the app. On Linux, start the server with `ollama serve` if it is not already running.
>
> Download the model:
>
> ```shell theme={"system"}
> ollama pull gemma4:e2b
> ```
>
> Send a request to your local server:
>
> > [tab] Ollama API
> >
> > ```shell theme={"system"}
> > curl http://localhost:11434/api/chat \
> >   -H "Content-Type: application/json" \
> >   -d '{
> >     "model": "gemma4:e2b",
> >     "messages": [
> >       {
> >         "role": "user",
> >         "content": "Say hello in one sentence."
> >       }
> >     ],
> >     "stream": false
> >   }'
> > ```
>
> > [tab] OpenAI Chat Completions
> >
> > ```shell theme={"system"}
> > curl http://localhost:11434/v1/chat/completions \
> >   -H "Content-Type: application/json" \
> >   -d '{
> >     "model": "gemma4:e2b",
> >     "messages": [
> >       {
> >         "role": "user",
> >         "content": "Say hello in one sentence."
> >       }
> >     ]
> >   }'
> > ```
> >
> > Read the answer from `choices[0].message.content`. See [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility.md) for client setup and supported features.
>
> > [tab] OpenAI Responses
> >
> > ```shell theme={"system"}
> > curl http://localhost:11434/v1/responses \
> >   -H "Content-Type: application/json" \
> >   -d '{
> >     "model": "gemma4:e2b",
> >     "input": "Say hello in one sentence."
> >   }'
> > ```
> >
> > Read the `output_text` content blocks inside `output`. The OpenAI Python client exposes the text as `response.output_text`.
> >
> > Responses requests are stateless: include conversation history in each request. `previous_response_id` and `conversation` aren't supported. See [Responses compatibility](https://docs.ollama.com/api/openai-compatibility.md#responses-api).
>
> > [tab] Anthropic Messages
> >
> > ```shell theme={"system"}
> > curl http://localhost:11434/v1/messages \
> >   -H "Content-Type: application/json" \
> >   -H "anthropic-version: 2023-06-01" \
> >   -d '{
> >     "model": "gemma4:e2b",
> >     "max_tokens": 1024,
> >     "messages": [
> >       {
> >         "role": "user",
> >         "content": "Say hello in one sentence."
> >       }
> >     ]
> >   }'
> > ```
> >
> > Read text blocks from `content`. See [Anthropic compatibility](https://docs.ollama.com/api/anthropic-compatibility.md) for client setup and supported features.

## Run a model locally

[Download Ollama](https://ollama.com/download), then run:

```shell theme={"system"}
ollama run gemma4:e2b
```

Ollama downloads the model and starts a chat on your computer. Type `/bye` to leave.

## Next steps

Add [tool calling](https://docs.ollama.com/capabilities/tool-calling.md), [stream responses](https://docs.ollama.com/capabilities/streaming.md), or browse [more models](https://ollama.com/search).
