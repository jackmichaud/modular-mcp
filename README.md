# 🌤️ Modular MCP Server & Client

This project provides a modular and extensible tool server built on `FastMCP`. It supports multiple tools organized across files and is compatible with a local or remote client that communicates via the MCP protocol.

## 📁 Project Structure
├── server.py             # Defines and exports the shared FastMCP instance
├── main.py               # Entry point to run the server
└── tools/
└── weather_tools.py  # Weather-related tools (alerts, forecast)

## 🚀 Getting Started

### 🔧 Requirements

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) package manager (used to run client/server scripts)
- MCP-compatible client and server setup

---

### Add Environment Variables

```bash
touch .env
echo "ANTHROPIC_API_KEY=<your key here>" >> .env
echo ".env" >> .gitignore
```

### 🖥️ Run the Server

To start the tool server:

```bash
uv run server/main.py
```

### 🧑‍💻 Run the Client

To start the client server:

```bash
uv run client/main.py <Path to server>
```

Replace ```<Path to server>``` with the local or remote path to the server script (e.g. server/main.py).

### 🧩 Extending the Server

You can easily extend this server with additional tools.
	1.	Create a new module in the tools/ directory (e.g., tools/finance_tools.py).
	2.	Define your functions using the @mcp.tool() decorator.
	3.	In config.yaml, add your new module to the tools list to register the tools.

Example:

```yaml
# config.yaml
tools:
  - tools.weather_tools
  - tools.search_tools  # Your new tools
```

