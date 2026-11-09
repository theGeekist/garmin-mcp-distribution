# Connect Garmin MCP to your assistant

[Connect your Garmin account](https://garmin.geekist.co/login), then follow the instructions for your client. Use `https://garmin.geekist.co/mcp` when asked for the remote MCP server URL.

| Client | Setup |
| --- | --- |
| ChatGPT | [Add a custom MCP server](https://garmin.geekist.co/help/chatgpt/) |
| Claude | [Add a custom connector](https://garmin.geekist.co/help/claude/) or [upload the plugin](#claude-plugin) |
| Codex | [Install the local marketplace](#codex) |
| Claude Code | [Install the local marketplace](#claude-code) |
| Gemini and Gemini CLI | [Add a custom app or install the CLI extension](gemini.md) |
| Grok | [Add a custom connector](grok.md) |
| Cursor | [Add the remote server](cursor.md) |

Custom connections and local package installation depend on your client version, plan and workspace policy. The guides describe manual setup. End-to-end authentication and tool availability vary by client.

## Codex

Download the [Codex marketplace ZIP](../../dist/archives/garmin-mcp-0.3.6-codex-marketplace.zip) and extract it. From the directory containing `.agents/plugins/marketplace.json`, run:

```sh
codex plugin marketplace add .
codex plugin add garmin-mcp@geekist-plugins
```

To add only the remote connection, run:

```sh
codex mcp add garmin-mcp --url https://garmin.geekist.co/mcp
```

Complete authentication if prompted. Start a new chat and ask Codex to show your most recent Garmin activity.

## Claude plugin

If your Claude account allows plugin uploads, go to **Customize → Plugins → Add → Upload plugin** and select the [Claude plugin ZIP](../../dist/archives/garmin-mcp-0.3.6-claude-plugin.zip). Open the plugin’s **Connectors** tab and connect Garmin MCP. [Claude plugin upload documentation](https://claude.com/docs/plugins/build#test-your-plugin)

## Claude Code

Download the [Claude Code marketplace ZIP](../../dist/archives/garmin-mcp-0.3.6-claude-code.zip) and extract it. From the directory containing `.claude-plugin/marketplace.json`, run:

```sh
claude plugin marketplace add .
claude plugin install garmin-mcp@geekist-plugins
```

Reload plugins, then run `/mcp` to inspect the connection and complete authentication. [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces)

## After connecting

Ask your assistant to show your latest Garmin activity. Available actions depend on the tools your client discovers and the permissions you grant. Review any proposed change before you confirm it, then check the result in Garmin Connect.

To stop access, disconnect Garmin in Geekist and remove the connection from your assistant. [Privacy policy](https://garmin.geekist.co/privacy/)

If you get stuck, tell Geekist which assistant you use and which step failed. Keep passwords, verification codes, tokens and health records out of the message. [Get help](https://garmin.geekist.co/support/)
