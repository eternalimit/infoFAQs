import test from "node:test";
import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import { createOriginRegister, registerOriginSource, createArtifactManifest, verifyArtifactManifest } from "../artifact-library.mjs";

const fakeReceipt = {
  engine: "CAT BOT Mine the Craft", engineVersion: "1.0.0",
  inventory: { stone: 0, crystal: 0, gold: 0, gem: 0 },
  craftedCount: 1,
  artifacts: [{ id: "artifact-000001", recipeId: "stone_brick", name: "Stone Brick", costs: { stone: 3 }, craftedOrdinal: 1 }]
};

test("origin register starts empty and explicitly preserves originals by reference", () => {
  const register = createOriginRegister();
  assert.equal(register.sources.length, 0);
  assert.match(register.policy, /source-reference-only/);
});

test("origin source requires filename and a SHA-256 receipt", () => {
  const register = createOriginRegister();
  assert.throws(() => registerOriginSource(register, { sourceId: "master-1", filename: "origin.png", sha256: "bad" }), /SHA-256/);
  const next = registerOriginSource(register, { sourceId: "master-1", filename: "origin.png", sha256: "a".repeat(64) });
  assert.equal(register.sources.length, 0);
  assert.equal(next.sources.length, 1);
  assert.match(next.sources[0].preservation, /not changed/);
});

test("duplicate origin source is rejected without mutating register", () => {
  let register = createOriginRegister();
  const source = { sourceId: "master-1", filename: "origin.png", sha256: "b".repeat(64) };
  register = registerOriginSource(register, source);
  assert.throws(() => registerOriginSource(register, source), /Duplicate/);
  assert.equal(register.sources.length, 1);
});

test("manifest is generated and independently verifies", async () => {
  const manifest = await createArtifactManifest(fakeReceipt, createOriginRegister(), webcrypto);
  const result = await verifyArtifactManifest(manifest, webcrypto);
  assert.equal(result.ok, true);
  assert.equal(result.artifactsVerified, 1);
  assert.equal(result.sourcesReferenced, 0);
  assert.match(manifest.manifestSha256, /^[a-f0-9]{64}$/);
});

test("manifest tampering is detected", async () => {
  const manifest = await createArtifactManifest(fakeReceipt, createOriginRegister(), webcrypto);
  manifest.artifacts[0].name = "Tampered";
  const result = await verifyArtifactManifest(manifest, webcrypto);
  assert.equal(result.ok, false);
  assert.match(result.reason, /mismatch/);
});
