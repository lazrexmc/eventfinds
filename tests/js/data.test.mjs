import { test } from "node:test";
import assert from "node:assert/strict";
import { fetchJson, FetchError, DataShapeError, assertShape } from "../../site/js/data.js";

const resp = (ok, status, body) => ({ ok, status, statusText: "S", json: async () => JSON.parse(body) });

test("fetchJson returns parsed JSON and passes no-cache", async () => {
  let seen;
  const f = async (p, o) => { seen = o; return resp(true, 200, '{"a":1}'); };
  assert.deepEqual(await fetchJson("/data/meta.json", f), { a: 1 });
  assert.equal(seen.cache, "no-cache");
});

test("fetchJson throws FetchError naming the path on HTTP error, bad JSON, network error", async () => {
  await assert.rejects(fetchJson("/data/x.json", async () => resp(false, 404, "")),
    (e) => e instanceof FetchError && e.path === "/data/x.json" && e.status === 404 && /404/.test(e.detail));
  await assert.rejects(fetchJson("/data/y.json", async () => resp(true, 200, "not json")),
    (e) => e instanceof FetchError && /JSON/.test(e.detail));
  await assert.rejects(fetchJson("/data/z.json", async () => { throw new Error("offline"); }),
    (e) => e instanceof FetchError && e.status === null && /offline/.test(e.detail));
});

test("assertShape rejects the wrong shape", () => {
  const meta = { event_count: 0, home: { name: "Columbia, MO", lat: 38.9, lng: -92.3 } };
  assertShape(meta, { events: [] });
  assert.throws(() => assertShape(meta, { events: "nope" }), DataShapeError);
  assert.throws(() => assertShape({ event_count: 0, home: {} }, { events: [] }), DataShapeError);
  assert.throws(() => assertShape({ home: meta.home }, { events: [] }), DataShapeError);
});
