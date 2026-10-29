# JOY Automart MCP Server

Official [Model Context Protocol](https://modelcontextprotocol.io) server for **[JOY Automart](https://www.joyautomart.com)**, Bangladesh's automotive parts and vehicle marketplace. It lets AI assistants (Claude, ChatGPT, Cursor and other MCP clients) search JOY's car-parts catalogue and JOY Auto Exchange vehicle listings, compare cars, look up a part, and prepare a purchase handoff for a human buyer. Prices are in BDT.

| | |
|---|---|
| **Remote endpoint** | `https://www.joyautomart.com/mcp` |
| **Transport** | Streamable HTTP (MCP protocol 2025-06-18 and later) |
| **Auth** | None for the public tools. Optional buyer token: `Authorization: Bearer joyagt_...` |
| **Docs** | https://www.joyautomart.com/developers |
| **Server card** | https://www.joyautomart.com/.well-known/mcp/server-card.json |

The server is hosted by JOY Automart; you do not need to run anything to use it. This repository contains the public metadata (registry `server.json`, Smithery config, tool snapshot) and a small **stdio proxy** for clients that only support local servers.

## Tools

Public, read-only tools (no account needed). Snapshot from a live `tools/list` call (see [`tools.json`](tools.json)); `*` marks a required argument.

| Tool | What it does | Arguments |
|---|---|---|
| `search_parts` | Search JOY Automart's automotive parts catalogue in Bangladesh. | `query`, `make`, `chassis`, `category`, `in_stock_only`, `include_rfq_catalogue`, `max_price_bdt`, `page`, `page_size` |
| `get_part` | Full public detail for one catalogue part: BDT price, stock, minimum order, verified offers and bulk price breaks. | `part_id`* |
| `search_vehicles` | Search JOY Auto Exchange vehicle listings in Bangladesh by make, model, year, fuel and BDT price. | `query`, `make`, `fuel_type`, `verified_only`, `include_unpriced`, `min_year`, `max_year`, `min_price_bdt`, `max_price_bdt`, `sort`, `page`, `page_size` |
| `get_vehicle` | Full public detail for one JOY Auto Exchange listing (by listing id or slug): BDT price, specs, photos and, when the car passed JOY's human QC, a summary of the inspection. | `vehicle_id`* |
| `get_auction_status` | Public status of one live or recent JOY auction: current bid in BDT, bid count, end time and anti-snipe extensions. | `auction_id`* |
| `compare_vehicles` | Side-by-side comparison of 2 to 4 listings (ids or slugs from search_vehicles): price, year, mileage, fuel, verification and inspection grade. | `vehicle_ids`* |
| `get_buying_guide` | How to buy from JOY Automart: currency (BDT), payment methods (card, bKash/Nagad/Rocket, cash on delivery), Dhaka and nationwide delivery zones and fees, human contact, and how an authenticated agent can place orders. | — |
| `prepare_buyer_handoff` | Compose the links a human buyer uses to complete a purchase: the product page and a pre-filled WhatsApp message with canonical part details and fitment limitations. | `part_id`*, `quantity`, `vehicle`, `note` |

All public tools are annotated `readOnlyHint: true`. **Fitment is guidance only:** the server never claims a part fits a vehicle without VIN/chassis evidence; confirm with JOY's sales team before buying.

With a buyer-issued agent token (create one at https://www.joyautomart.com/cars/account?section=ai-agents&portal=retail) an agent can also use `quote_order`, `place_order` (cash on delivery or approved trade credit, within the buyer's spending limits), `create_rfq`, `get_order_status` and `list_my_orders`.

## Connect

### Claude (claude.ai / Claude Desktop)
Settings → Connectors → **Add custom connector** → URL `https://www.joyautomart.com/mcp`.

### ChatGPT
Settings → Connectors (developer mode) → **Create** → MCP server URL `https://www.joyautomart.com/mcp`, authentication: none.

### Cursor
`~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "joy-automart": { "url": "https://www.joyautomart.com/mcp" }
  }
}
```

### VS Code / any client with remote HTTP support
```json
{
  "servers": {
    "joy-automart": { "type": "http", "url": "https://www.joyautomart.com/mcp" }
  }
}
```

### Claude Code
```bash
claude mcp add --transport http joy-automart https://www.joyautomart.com/mcp
```

### Quick test with curl
```bash
curl -s https://www.joyautomart.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Local stdio proxy (npx) — coming soon

The npm package `@joyautomart/mcp-server` is **not published yet**. Once it is, stdio-only clients can use:

```json
{
  "mcpServers": {
    "joy-automart": {
      "command": "npx",
      "args": ["-y", "@joyautomart/mcp-server"],
      "env": { "JOY_AGENT_TOKEN": "joyagt_your_token_here" }
    }
  }
}
```

Until then you can run the proxy from this repo (Node 18+):

```bash
git clone https://github.com/www-joyautomart-com/mcp-server && cd mcp-server
npm ci
node bin/joyautomart-mcp.js            # or: --url https://www.joyautomart.com/mcp
```

`JOY_AGENT_TOKEN` is optional; public tools work without it.

## Listings
- Official MCP Registry name: `com.joyautomart/mcp` ([server.json](server.json); listing pending domain verification)
- Smithery config: [smithery.yaml](smithery.yaml)

## Support
Questions about parts, orders or fitment: https://www.joyautomart.com. Issues with this repository: [GitHub issues](https://github.com/www-joyautomart-com/mcp-server/issues).

## License
[MIT](LICENSE) © 2026 JOY Automart / Ahmed Joyadh
