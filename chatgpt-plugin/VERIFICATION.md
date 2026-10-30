# Verification — 30 October 2026

The candidate uses JOY Automart MCP server version **1.2.0** at
`https://www.joyautomart.com/mcp` with **no authentication**. Source baseline:
`www-joyautomart-com/mcp-server` commit `7d45556b636ec5c0347a2bceb1d04c946b57445c`.

## Direct server checks

The official `@modelcontextprotocol/sdk` JavaScript client connected using
Streamable HTTP. `scripts/verify-chatgpt-plugin.mjs` completed eight checks with
**8 Passed, 0 Failed**. These results do not establish ChatGPT model behaviour.

| Check | Result | Observed evidence |
| --- | --- | --- |
| Public inventory and tool annotations | Passed | Exactly 8 tools; all read-only, non-destructive; boolean open-world annotations present |
| English parts search with price and make filters | Passed | 3 Toyota brake-pad candidates at positive prices no greater than BDT 10,000; fitment warning included |
| Bangla search | Passed | Bangla request interpreted as Toyota Axio brake pad; 1 candidate returned |
| Search then vehicle comparison | Passed | Filtered Toyota listings met the year and BDT limits; comparison used two returned IDs |
| Vehicle detail | Passed | Detail retrieved for the actual first returned listing; recorded verification state retained |
| Part detail, buying guide and handoff | Passed | Actual part detail, Bangladesh buying terms and prepared product/WhatsApp links returned |
| Unavailable auction recovery | Passed | Missing test auction returned an error; no fabricated live auction |
| Comparison schema boundary | Passed | One-item comparison rejected below the advertised two-item minimum |

The auction check tested an unavailable/missing auction. It did **not** test a
successful live auction or bidding. No purchase, RFQ, message, payment, stock
reservation or bid was created. Price and inventory observations are a snapshot,
not a guarantee of present availability.

## Package and listing

The builder inspected the actual ZIP and passed structural checks: manifest
syntax and schema declarations, exact category, 23-character subtitle, starter
prompt lengths, five positive and three negative cases, global directory
targeting, one HTTPS MCP server with authentication None, no private app
bindings, and actual contained 512 × 512 PNG assets. The existing website icon
was rendered without changing its design and visually inspected.

The four listing destinations returned public HTML without login and their
contents were inspected. Privacy explicitly describes the MCP connector,
request data and 90-day connector record retention. Terms name the proprietor
and platform commerce conditions. The customer-service page supplies human
telephone/WhatsApp contact; no support call or message was placed.

## Existing third-party directory approval

The owner's connected inbox contains an email from `contact@mcpservers.org`
dated 30 October 2026, 01:20 UTC (07:20 Bangladesh time), confirming approval
of **JOY Automart MCP Server** and saying the following listing is live:
https://mcpservers.org/servers/www-joyautomart-com/mcp-server.

This verifies what the directory communicated. Independent page retrieval was
blocked (HTTP 403), so current public-page rendering was not verified. The
approval is from mcpservers.org; it does not establish OpenAI plugin approval.
A targeted search of the connected inbox found no OpenAI plugin approval email.
No private email body or mailbox metadata is included in the public plugin ZIP.

## Still unverified or incomplete

- Intended verified developer identity and final public developer name.
- Owner confirmation of the proposed commerce declaration.
- Actual ChatGPT/Codex execution of the five positive and three negative prompts.
- Real demo recording, accessible hosting and playback verification.
- Final saved public submission connection, scans, domain/developer verification
  and applicable legal/policy attestations.
- OpenAI review, approval and publication.

**The package is a working draft candidate, not submission-ready or publicly
available.** Plugin Creator was used for its creation and submission workflow;
its private account-save operation was intentionally not substituted for a
public directory submission.
