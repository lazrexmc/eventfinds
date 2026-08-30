// data.js - the fetch layer. One property is load-bearing: a failed fetch THROWS a typed error and
// never resolves to anything a caller could mistake for an empty result (static-publication-site
// trap 6.1). Same-origin static JSON only; there is no key and no config to blank.

export class FetchError extends Error {
  constructor(path, status, detail) {
    super("fetch of " + path + " failed: " + detail);
    this.name = "FetchError";
    this.path = path;      // named in the error box
    this.status = status;  // HTTP status, or null when the request never completed
    this.detail = detail;
  }
}

export class DataShapeError extends Error {
  constructor(message) { super(message); this.name = "DataShapeError"; }
}

export async function fetchJson(path, fetchImpl = globalThis.fetch) {
  let resp;
  try {
    resp = await fetchImpl(path, { cache: "no-cache" });
  } catch (err) {
    throw new FetchError(path, null, "network error (" + (err && err.message ? err.message : String(err)) + ")");
  }
  if (!resp.ok) {
    throw new FetchError(path, resp.status, "HTTP " + resp.status + (resp.statusText ? " " + resp.statusText : ""));
  }
  try {
    return await resp.json();
  } catch (err) {
    throw new FetchError(path, resp.status, "response is not valid JSON (" + (err && err.message ? err.message : String(err)) + ")");
  }
}

export function assertShape(meta, eventsDoc) {
  if (!eventsDoc || !Array.isArray(eventsDoc.events)) {
    throw new DataShapeError("data/events.json does not carry an events array");
  }
  const h = meta && meta.home;
  if (!h || !Number.isFinite(h.lat) || !Number.isFinite(h.lng)) {
    throw new DataShapeError("data/meta.json has no numeric home.lat / home.lng");
  }
  if (typeof meta.event_count !== "number") {
    throw new DataShapeError("data/meta.json has no numeric event_count");
  }
}
