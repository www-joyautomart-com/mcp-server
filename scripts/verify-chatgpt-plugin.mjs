#!/usr/bin/env node
// Public read-only checks via the official MCP client. This is not an in-host model test.
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const outputArg = process.argv.indexOf('--output');
const out = path.resolve(outputArg < 0 ? '/tmp/joy-plugin-check' : process.argv[outputArg + 1]);
await mkdir(out, { recursive: true });
const records = [];
const client = new Client({ name: 'joy-public-plugin-verification', version: '1.0.0' });
const transport = new StreamableHTTPClientTransport(new URL('https://www.joyautomart.com/mcp'));
const expectedNames = [
  'search_parts', 'get_part', 'search_vehicles', 'get_vehicle',
  'get_auction_status', 'compare_vehicles', 'get_buying_guide', 'prepare_buyer_handoff'
];

async function evidence(name, data) {
  await writeFile(path.join(out, `${name}.json`), JSON.stringify(data, null, 2) + '\n');
}

async function call(name, args, label) {
  assert(expectedNames.includes(name), 'Only the eight public read tools may be called');
  const request = { name, arguments: args };
  const result = await client.callTool(request);
  await evidence(label, { request, result });
  assert(!result.isError, `${label}: server returned a tool error`);
  const data = result.structuredContent ?? JSON.parse(result.content.find(c => c.type === 'text').text);
  return data;
}

async function check(id, fn) {
  try {
    const note = await fn();
    records.push({ id, layer: 'official-mcp-sdk', status: 'Passed', note });
  } catch (err) {
    records.push({ id, layer: 'official-mcp-sdk', status: 'Failed', note: String(err) });
  }
  console.log(JSON.stringify(records.at(-1)));
}

try {
  await client.connect(transport);
  const inventory = await client.listTools();
  await evidence('tools-list-sdk', inventory);
  await check('public-tool-inventory', async () => {
    assert.deepEqual(inventory.tools.map(t => t.name).sort(), [...expectedNames].sort());
    for (const t of inventory.tools) {
      for (const key of ['readOnlyHint', 'openWorldHint', 'destructiveHint']) {
        assert.equal(typeof t.annotations?.[key], 'boolean', `${t.name}.${key}`);
      }
      assert.equal(t.annotations.readOnlyHint, true);
      assert.equal(t.annotations.destructiveHint, false);
    }
    return 'Exactly eight unauthenticated public read tools with required boolean annotations';
  });

  // These independent reads may run concurrently. Dependent detail/handoff calls follow.
  const reads = await Promise.allSettled([
    call('search_parts', { query: 'brake pads', make: 'Toyota', max_price_bdt: 10000, page_size: 3 }, 'parts-english'),
    call('search_parts', { query: 'টয়োটা এক্সিও ব্রেক প্যাড', page_size: 3 }, 'parts-bangla'),
    call('search_vehicles', { make: 'Toyota', min_year: 2015, max_price_bdt: 7000000, page_size: 4 }, 'vehicles'),
    call('get_buying_guide', {}, 'buying-guide')
  ]);
  function read(i) {
    if (reads[i].status !== 'fulfilled') throw reads[i].reason;
    return reads[i].value;
  }

  await check('P1-english-search-server', async () => {
    const d = read(0);
    assert.equal(d.currency, 'BDT');
    assert(Array.isArray(d.items) && d.items.length <= 3);
    assert.equal(d.page_size, 3);
    for (const item of d.items) {
      assert(typeof item.price_bdt === 'number' && item.price_bdt > 0 && item.price_bdt <= 10000);
      assert(item.url.startsWith('https://www.joyautomart.com/'));
      assert(item.fitment_candidates.some(c => c.make.toLowerCase() === 'toyota'));
    }
    assert(d.fitment_notice.toLowerCase().includes('not a fitment guarantee'));
    return `${d.items.length} matching BDT-priced candidates; fitment warning present`;
  });

  await check('P2-bangla-search-server', async () => {
    const d = read(1);
    assert.equal(d.currency, 'BDT');
    assert(Array.isArray(d.items));
    assert(d.query_interpreted_as.toLowerCase().includes('axio'));
    return `Bangla query interpreted as ${d.query_interpreted_as}; ${d.items.length} results`;
  });

  await check('P3-vehicle-comparison-server', async () => {
    const d = read(2);
    assert.equal(d.currency, 'BDT');
    assert(d.items.length >= 2, 'At least two live fixtures required for comparison');
    for (const item of d.items) {
      assert.equal(item.make, 'Toyota');
      assert(item.year >= 2015 && item.price_bdt > 0 && item.price_bdt <= 7000000);
    }
    const ids = d.items.slice(0, 2).map(v => v.listing_id);
    const comparison = await call('compare_vehicles', { vehicle_ids: ids }, 'compare');
    const serialized = JSON.stringify(comparison);
    for (const id of ids) assert(serialized.includes(id));
    return `Compared two IDs from actual filtered search: ${ids.join(', ')}`;
  });

  await check('P4-vehicle-detail-server', async () => {
    const chosen = read(2).items[0];
    assert(chosen, 'A current live vehicle fixture is required');
    const d = await call('get_vehicle', { vehicle_id: chosen.listing_id }, 'vehicle-detail');
    assert(JSON.stringify(d).includes(chosen.listing_id));
    assert(JSON.stringify(d).includes(chosen.model));
    return `Retrieved actual listing ${chosen.listing_id}; raw verification state saved for host review`;
  });

  await check('P5-human-handoff-server', async () => {
    const part = read(1).items[0];
    assert(part, 'A current live part fixture is required');
    const detail = await call('get_part', { part_id: part.part_id }, 'part-detail');
    assert(JSON.stringify(detail).includes(part.part_id));
    const guide = read(3);
    assert.equal(guide.market, 'Bangladesh');
    assert.equal(guide.currency, 'BDT');
    assert(Array.isArray(guide.payment_methods) && guide.payment_methods.length > 0);
    assert(Array.isArray(guide.delivery_zones) && guide.delivery_zones.length > 0);
    const handoff = await call('prepare_buyer_handoff', {
      part_id: part.part_id, quantity: 2, vehicle: 'Toyota Axio'
    }, 'buyer-handoff');
    const serialized = JSON.stringify(handoff);
    assert(serialized.includes(part.part_id));
    assert(serialized.includes('https://wa.me/8801886799533'));
    assert(serialized.includes('https://www.joyautomart.com/'));
    return `Part ${part.part_id}; real detail, buying terms and prepared purchase URLs returned; no message sent`;
  });

  await check('auction-missing-fixture-recovery', async () => {
    const request = { name: 'get_auction_status', arguments: { auction_id: 'joy-review-no-such-auction-20261030' } };
    const result = await client.callTool(request);
    await evidence('auction-unavailable', { request, result });
    assert(result.isError, 'A non-existent auction must not be represented as a live one');
    return 'Missing/unavailable auction reports a tool error; a successful live-auction fixture was not tested';
  });

  await check('schema-invalid-comparison', async () => {
    try {
      const result = await client.callTool({ name: 'compare_vehicles', arguments: { vehicle_ids: ['one-only'] } });
      await evidence('invalid-comparison', result);
      assert(result.isError, 'One-item comparison must be rejected');
    } catch (err) {
      assert.equal(err.code, -32602, 'Expected JSON-RPC invalid params rejection');
      await evidence('invalid-comparison', { error: String(err), code: err.code });
    }
    return 'Server rejected a comparison below its advertised two-listing minimum';
  });
} catch (err) {
  records.push({ id: 'connection', layer: 'official-mcp-sdk', status: 'Failed', note: String(err) });
} finally {
  await client.close().catch(() => {});
}

const summary = {
  checked_at: new Date().toISOString(), endpoint: 'https://www.joyautomart.com/mcp', authentication: 'none',
  results: records,
  host_review_cases: { positive: 'Not run in ChatGPT/Codex', negative: 'Not run in ChatGPT/Codex' },
  demo_recording: 'Not recorded', public_submission: 'Not uploaded or submitted',
  limitation: 'These are direct SDK server checks, not model tool-selection or final saved portal-version checks.'
};
await evidence('verification-summary', summary);
console.log(JSON.stringify({ passed: records.filter(r => r.status === 'Passed').length, failed: records.filter(r => r.status === 'Failed').length, output: out }));
if (records.some(r => r.status === 'Failed')) process.exitCode = 1;
