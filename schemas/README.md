# Package schemas

The two Agent Plugins 1.0.0 schema files are snapshots of the versioned schemas for [plugin.json](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) and [mcp.json](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json). CI validates portable OpenAI manifests against these local copies so package checks can run without fetching schemas. When updating a snapshot, compare it with the upstream version and rerun the package checks.

The base MCP schema validates the portable endpoint declaration. OpenAI's developer portal separately validates provider-specific submission metadata and OAuth. Claude Code has its own plugin and marketplace validator.
