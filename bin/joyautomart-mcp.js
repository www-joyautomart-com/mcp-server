#!/usr/bin/env node
// stdio <-> Streamable HTTP proxy for JOY Automart's MCP server.
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const args = process.argv.slice(2);
let url = process.env.JOY_MCP_URL || "https://www.joyautomart.com/mcp";
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--url") url = args[++i];
  else if (args[i].startsWith("--url=")) url = args[i].slice(6);
  else if (args[i] === "--help" || args[i] === "-h") {
    console.error("Usage: joyautomart-mcp-server [--url https://www.joyautomart.com/mcp]\nEnv: JOY_AGENT_TOKEN (optional buyer token joyagt_...)");
    process.exit(0);
  }
}
const token = process.env.JOY_AGENT_TOKEN;
const headers = token ? { Authorization: `Bearer ${token}` } : {};
const log = (...m) => console.error("[joyautomart-mcp]", ...m);

const remote = new StreamableHTTPClientTransport(new URL(url), { requestInit: { headers } });
const local = new StdioServerTransport();

local.onmessage = (msg) => remote.send(msg).catch((e) => {
  log("upstream error:", e.message);
  if (msg.id !== undefined && msg.method) {
    local.send({ jsonrpc: "2.0", id: msg.id, error: { code: -32603, message: `Upstream error: ${e.message}` } });
  }
});
remote.onmessage = (msg) => local.send(msg);
remote.onerror = (e) => log("remote:", e.message);
local.onclose = async () => { await remote.close().catch(() => {}); process.exit(0); };
remote.onclose = () => {};

await remote.start();
await local.start();
log(`proxying stdio -> ${url}${token ? " (authenticated)" : ""}`);
