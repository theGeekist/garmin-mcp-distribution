# Connect Grok

1. [Connect your Garmin account](https://garmin.geekist.co/login).
2. Open [Grok Connectors](https://grok.com/connectors) and choose **New Connector → Custom**.
3. Enter `https://garmin.geekist.co/mcp` and follow the sign-in and permission prompts.
4. Start a conversation and ask Grok to use the connector to show your latest Garmin activity.

On Grok Business or Enterprise, ask your team administrator to add the connector before you connect it. [Grok connector documentation](https://docs.x.ai/grok/connectors) · [Workspace connector management](https://docs.x.ai/grok/connector-management)

For Grok Build, add the remote server from the terminal and follow the sign-in prompt when you first use it. [Grok Build MCP documentation](https://docs.x.ai/build/features/mcp-servers)

```sh
grok mcp add --transport http garmin-mcp https://garmin.geekist.co/mcp
```
