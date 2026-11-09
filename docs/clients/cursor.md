# Connect Cursor

[Connect your Garmin account](https://garmin.geekist.co/login), then add this server to your global `~/.cursor/mcp.json` or your project’s `.cursor/mcp.json`. If the file already lists servers, add the `garmin-geekist` entry inside its existing `mcpServers` object.

```json
{
  "mcpServers": {
    "garmin-geekist": {
      "url": "https://garmin.geekist.co/mcp"
    }
  }
}
```

Refresh MCP connections in Cursor and follow the sign-in prompt if shown. Check that `garmin-geekist` is connected, then ask Cursor to show your latest Garmin activity. [Cursor MCP documentation](https://cursor.com/docs/mcp)
