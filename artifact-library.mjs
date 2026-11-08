/**
 * MASTER.ORIGIN artifact manifest and preservation register.
 * Records references and hashes; it never edits or replaces source files.
 */
function canonicalize(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonicalize).join(",") + "]";
  return "{" + Object.keys(value).sort().map(key => JSON.stringify(key) + ":" + canonicalize(value[key])).join(",") + "}";
}

function validSha256(value) {
  return typeof value === "string" && /^[a-f0-9]{64}$/i.test(value);
}

function hex(bytes) {
  return Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, "0")).join("");
}

async function digest(value, cryptoProvider = globalThis.crypto) {
  if (!cryptoProvider?.subtle) throw new Error("Web Crypto SHA-256 is unavailable in this context.");
  return hex(await cryptoProvider.subtle.digest("SHA-256", new TextEncoder().encode(canonicalize(value))));
}

export function createOriginRegister() {
  return { schema: "MASTER.ORIGIN/1.0", policy: "source-reference-only; originals are not modified", sources: [] };
}

export function registerOriginSource(register, source) {
  if (!register || register.schema !== "MASTER.ORIGIN/1.0" || !Array.isArray(register.sources)) {
    throw new TypeError("Invalid MASTER.ORIGIN register.");
  }
  if (!source || typeof source.sourceId !== "string" || !source.sourceId.trim()) {
    throw new TypeError("A sourceId is required.");
  }
  if (register.sources.some(item => item.sourceId === source.sourceId)) {
    throw new Error("Duplicate sourceId; original register remains unchanged.");
  }
  if (!validSha256(source.sha256)) throw new TypeError("A verified 64-character SHA-256 is required.");
  if (typeof source.filename !== "string" || !source.filename.trim()) {
    throw new TypeError("Original filename is required.");
  }
  const next = structuredClone(register);
  next.sources.push({
    sourceId: source.sourceId,
    filename: source.filename,
    sha256: source.sha256.toLowerCase(),
    sourceLocation: source.sourceLocation || "not supplied",
    preservation: "reference-only; source bytes not changed",
    verification: "hash supplied; independent byte verification pending"
  });
  return next;
}

export async function createArtifactManifest(craftReceipt, originRegister = createOriginRegister(), cryptoProvider = globalThis.crypto) {
  if (!craftReceipt || craftReceipt.engine !== "CAT BOT Mine the Craft") {
    throw new TypeError("A valid CAT BOT craft receipt is required.");
  }
  if (!originRegister || originRegister.schema !== "MASTER.ORIGIN/1.0" || !Array.isArray(originRegister.sources)) {
    throw new TypeError("A valid MASTER.ORIGIN register is required.");
  }
  const artifacts = [];
  for (const artifact of craftReceipt.artifacts) {
    artifacts.push({ ...artifact, artifactSha256: await digest(artifact, cryptoProvider) });
  }
  const body = {
    schema: "YCI-ARTIFACT-MANIFEST/1.0",
    createdAt: new Date().toISOString(),
    engine: craftReceipt.engine,
    engineVersion: craftReceipt.engineVersion,
    inventory: { ...craftReceipt.inventory },
    craftedCount: craftReceipt.craftedCount,
    artifacts,
    originRegister: structuredClone(originRegister),
    preservationNotice: "MASTER.ORIGIN sources are references only. No original source bytes are included, edited, or replaced."
  };
  return { ...body, manifestSha256: await digest(body, cryptoProvider) };
}

export async function verifyArtifactManifest(manifest, cryptoProvider = globalThis.crypto) {
  if (!manifest || manifest.schema !== "YCI-ARTIFACT-MANIFEST/1.0" || !validSha256(manifest.manifestSha256)) {
    return { ok: false, reason: "Manifest schema or digest is missing." };
  }
  const { manifestSha256, ...body } = manifest;
  const actual = await digest(body, cryptoProvider);
  if (actual !== manifestSha256.toLowerCase()) return { ok: false, reason: "Manifest SHA-256 mismatch." };
  for (const artifact of manifest.artifacts || []) {
    const { artifactSha256, ...record } = artifact;
    if (!validSha256(artifactSha256) || await digest(record, cryptoProvider) !== artifactSha256.toLowerCase()) {
      return { ok: false, reason: "Artifact digest mismatch: " + (artifact.id || "unnamed artifact") };
    }
  }
  return { ok: true, manifestSha256: actual, artifactsVerified: (manifest.artifacts || []).length, sourcesReferenced: manifest.originRegister.sources.length };
}
