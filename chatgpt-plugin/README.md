# JOY Automart for ChatGPT and Codex

This is the public-directory plugin source for JOY Automart's existing remote
MCP server. It reuses JOY's production endpoint on Oracle. No separate server,
hosting provider, private app ID, API key or payment credential is packaged.

**Status: built candidate; not submitted, approved or publicly listed.**

## What users can do

- Search car parts in English, Bangla or Banglish, with BDT prices and stock.
- Read part details, minimum quantities and the returned fitment limitations.
- Search public vehicle listings and read their actual verification status.
- Compare two to four returned vehicles.
- Read Bangladesh payment and delivery terms.
- Prepare a product link or an unsent WhatsApp message for JOY's team.
- Read public auction status when auctions are available; no bidding.

The package uses `auth.type: none`, so only the eight public tools are exposed.
Authenticated buyer-agent ordering is a separate JOY feature. Public directory
targeting has no country restriction, as requested. This does not expand JOY's
shipping territory: the catalogue and buying terms are for Bangladesh.

## Build and verify

From the repository root:

```sh
npm ci --ignore-scripts
node scripts/verify-chatgpt-plugin.mjs --output /tmp/joy-plugin-check
python3 scripts/build-chatgpt-plugin.py --output /tmp/JOY_Automart_ChatGPT_Plugin_v1.0.0_DRAFT.zip
```

On Node 24+, use `node --use-env-proxy` where the environment requires its
configured HTTP proxy. Preserve the environment's CA trust. The verifier only
uses public read-only tools, validates returned data and saves raw evidence.
It never submits a buyer token, purchase, payment, message or bid.

The builder inspects the actual ZIP, field lengths, PNG dimensions, single MCP
configuration and five-positive/three-negative review metadata. Passing this
check establishes package structure, not approval or public submission readiness.

## Complete the submission materials

1. Choose the intended verified publisher identity in your OpenAI developer
   account. JOY Automart is the proposed business branding. The candidate
   intentionally omits `interface.developerName` until that identity is confirmed.
2. Confirm the proposed commerce declaration: users discover physical parts and
   vehicles and continue on JOY's website or with JOY's human team. This release
   performs no in-chat checkout.
3. Rehearse and record the real plugin in ChatGPT or Codex using [the demo
   walkthrough](DEMO_WALKTHROUGH.md). Host the actual recording at a
   reviewer-accessible HTTPS URL, verify playback, and add that URL as
   `extensions.com.openai.review.demo_recording_url`.
4. Rebuild the ZIP. Only when these materials are complete, upload it in the
   official plugin submission dashboard under the intended verified publisher.
   Connect the existing HTTPS MCP server without authentication. Inspect the
   saved metadata, run the review cases against that exact saved version, and
   resolve required metadata, skill and tool scans.
5. Complete domain verification with the portal's actual challenge token if
   requested. Any production change follows JOY's existing Oracle deployment
   process from the owner's Windows shell. This package performs no deployment.
6. The authorised developer completes the required legal/policy attestations and
   submits for review. After approval, publishing the approved version is a
   separate action.

Do not upload the entire source/release kit as the plugin. The public-upload ZIP
contains only `joy-automart/plugin.json`, `mcp.json` and its referenced PNG asset.
Do not include private credentials or reviewer-account passwords in any archive.
This public connection needs no reviewer login; final portal connection testing
is still required.

Official guidance:
https://developers.openai.com/plugins/deploy/submission

## Verified listing destinations

All four destinations were fetched without login and their page content was
inspected on 30 October 2026. Their availability can change.

| Field | Destination | Observed purpose |
| --- | --- | --- |
| Website | https://www.joyautomart.com/developers | Names JOY, the actual MCP endpoint, tools, access and support |
| Support | https://www.joyautomart.com/customer-service | Parts/order help plus human telephone and WhatsApp contact |
| Privacy | https://www.joyautomart.com/privacy | Explicit connector request logging, data use, retention and privacy contact |
| Terms | https://www.joyautomart.com/terms | Platform commerce terms, human approvals and proprietor/contact identity |

These published policies are reused rather than drafting unsupported retention,
support or legal promises. Publisher legal review and portal attestations have
not been performed by this package.

## Branding

The square PNG is rendered from JOY's existing public
`https://www.joyautomart.com/joy-automart-icon.svg`, preserving the existing mark.
It is 512 × 512 pixels. MAISON burgundy `#A4123A` is the configured brand colour.
No replacement logo or dark-mode artwork was invented.
