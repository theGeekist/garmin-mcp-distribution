# Connect Gemini

Gemini and Gemini CLI have separate setup paths. [Connect your Garmin account](https://garmin.geekist.co/login) first.

## Gemini app

1. Open Gemini on the web and go to **Settings → Connected Apps**. If needed, open **Personal Intelligence** first.
2. Under **Custom apps**, add `https://garmin.geekist.co/mcp` and follow the sign-in and consent prompts.
3. In a chat, type `@` and select the connected app. Ask it to show your latest Garmin activity.

Google limits custom apps by account, region, age and activity settings. [Gemini custom app requirements](https://support.google.com/gemini/answer/17209137)

## Gemini CLI

Download the [Gemini CLI extension ZIP](../../dist/archives/garmin-mcp-0.3.6-gemini-cli.zip) and extract it. Pass the directory containing `gemini-extension.json` to the installer:

```sh
gemini extensions install /path/to/extracted/garmin-mcp
```

Restart Gemini CLI and run `/mcp list` to check the connection. If prompted, run `/mcp auth garmin-mcp` and complete sign-in in your browser. Then ask for your latest Garmin activity. [Gemini CLI MCP documentation](https://geminicli.com/docs/tools/mcp-server/)
