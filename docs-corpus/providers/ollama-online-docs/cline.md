> ## Documentation Index
> Fetch the complete documentation index at: https://docs.ollama.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Cline

## Install

Install [Cline](https://docs.cline.bot/getting-started/installing-cline) in your IDE.

## Usage with Ollama

1. Open Cline settings > `API Configuration` and set `API Provider` to `Ollama`
2. Select a model under `Model` or type one (e.g. `qwen3`)
3. Update the context window to at least 32K tokens under `Context Window`

> [!NOTE]
>
> Use a [context window](https://docs.ollama.com/context-length.md) of at least 32K tokens for coding.

![Cline settings configuration showing API Provider set to Ollama](https://mintcdn.com/ollama-9269c548/DILXUjvsEb6UDNxN/images/cline-settings.png?fit=max\&auto=format\&n=DILXUjvsEb6UDNxN\&q=85\&s=2d2755de6b2e06cd513119abf389acd0)

## Connecting to ollama.com

1. Create an [API key](https://ollama.com/settings/keys) from ollama.com
2. Click on `Use custom base URL` and set it to `https://ollama.com`
3. Enter your **Ollama API Key**
4. Select a model from the list

### Models

Choose a [cloud model](https://ollama.com/search?c=cloud) that supports tool calling.
