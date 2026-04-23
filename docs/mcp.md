# MCP Servers

Links to GitHub Copilot MCP servers:

* **Labels:** https://api.githubcopilot.com/mcp/x/labels
* **Issues:** https://api.githubcopilot.com/mcp/x/issues

The list of all available GitHub Copilot MCP servers can be found [here](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)

## How to insert server

1. Create `.vscode` folder in the root of your project if it doesn't exist.
2. Create `mcp.json` file in the `.vscode` folder.
3. Paste the following code snippet into the `mcp.json` file:


```json
{
	"inputs": [],
	"servers": {
		"gh-labels": {
			"type": "http",
			"url": "https://api.githubcopilot.com/mcp/x/labels"
		},
		"gh-issues": {
			"type": "http",
			"url": "https://api.githubcopilot.com/mcp/x/issues"
		}
	}
}
```