# Record the actual JOY Automart plugin

**This is a recording guide, not a completed video.** No demo URL is supplied
until a real recording is available and its playback and permissions are checked.

Use ChatGPT or Codex with a development connection to
`https://www.joyautomart.com/mcp`, Streamable HTTP, authentication None. Reuse a
working development connection if one exists. Do not create a second private
plugin or an incomplete public submission merely to record the demo.

If a development installation is unavailable, establish that connection through
the host's supported development/plugin flow first. Connection, tool availability
and user eligibility must be verified in the actual host. This preparation run
tested the remote server with the official MCP JavaScript SDK; it did not test
the saved public submission inside ChatGPT.

## Capture a 3–5 minute walkthrough

Use Windows screen recording (Snipping Tool video capture or Win+Alt+R, where
available). Capture the app window and readable prompts/results. Hide personal
tabs, email, tokens, saved payment information and unrelated conversations.
Computer control or screenshots alone do not create a video recording.

| Step | Prompt or action | Show on screen |
| --- | --- | --- |
| 1 | Show the JOY Automart development connection | Actual endpoint, no authentication, public tools available |
| 2 | Find Toyota brake pads below BDT 10,000. Show current prices and explain whether fitment is confirmed. | Real `search_parts` results, BDT amounts, JOY links, fitment and source-verification limits |
| 3 | টয়োটা এক্সিও ব্রেক প্যাড খুঁজে দিন। | Actual Bangla search and a readable Bangla response |
| 4 | Find Toyota cars from 2015 onward under BDT 7,000,000 and compare two listings. | Real search IDs used in comparison; unknown mileage or inspection remains unknown |
| 5 | Show the published details and inspection status for the first Toyota car you found. | Actual `get_vehicle` output and its returned verification state |
| 6 | Find Toyota Axio brake pads, then prepare a link to ask JOY about two sets and explain delivery and payment options. | Part detail, buying terms, actual purchase links and clear statement that no message/order/payment was made |
| 7 | Buy those brake pads now and charge my saved card without sending me to a website. | Clear unsupported-action explanation; no charge, order or fabricated confirmation |

Let results remain visible long enough to read. If stock changes, show the true
empty or unavailable response and appropriate recovery. Do not replace it with
a mockup. Rehearse before recording and address failures first.

## Verify and host

1. Play the saved video all the way through. Confirm readable prompts and real
   results, audible narration if used, and no exposed secrets.
2. Upload it to the owner's chosen reviewer-accessible video destination.
   Loom, an unlisted YouTube video, or an HTTPS video on the owner's site can
   work if it opens and plays without a private login. Do not publish private
   account information.
3. Open the actual URL without an authenticated session and verify playback and
   reviewer access. A title page, script or sign-in wall is insufficient.
4. Add that exact HTTPS URL to `review.demo_recording_url`, then rebuild and
   inspect the upload ZIP.

The five positive and three negative cases are already in `plugin.json`. Run
them in the host against the final saved submission as well. Direct SDK tests
prove server behaviour; they do not prove the model's final answers or tool
selection. Negative prompts in particular remain unrun until tested in-host.
