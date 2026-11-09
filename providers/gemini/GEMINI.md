# Garmin MCP by geekist.co

Use the `garmin-mcp` MCP server's discovered tools for the user's request. The live service is at `https://garmin.geekist.co/mcp`; available tools depend on the connected account. Follow each tool's schema and explain its effect before acting. Get the user's explicit confirmation before creating, editing, uploading or deleting Garmin data, or disconnecting the account. Do not claim a change succeeded unless the service confirms the outcome.

Use the bundled `garmin-review` skill for supported workflows. After each Garmin tool call, inspect its result for `serviceAnnouncements` and present any actual notices clearly. Use feedback and owner-notice tools when they are exposed and relevant; do not claim feedback submission or message delivery unless the tool result confirms it. Client and OAuth compatibility may vary; follow the authentication flow presented by Gemini and use only tools it actually discovers.
