import test from "node:test";
import assert from "node:assert/strict";
import {
  createCraftState, addResource, canCraft, craft,
  createCraftReceipt, assertCraftState
} from "../craft-engine.mjs";

test("new craft state starts with zero inventory and no artifacts", () => {
  const state = createCraftState();
  assert.deepEqual(state.inventory, { stone: 0, crystal: 0, gold: 0, gem: 0 });
  assert.equal(state.craftedCount, 0);
  assert.equal(assertCraftState(state), true);
});

test("mined resources are added without mutating the original state", () => {
  const initial = createCraftState();
  const next = addResource(initial, "Stone", 3);
  assert.equal(initial.inventory.stone, 0);
  assert.equal(next.inventory.stone, 3);
});

test("unknown resources and invalid quantities are rejected", () => {
  assert.throws(() => addResource(createCraftState(), "uranium", 1), /Unknown resource/);
  assert.throws(() => addResource(createCraftState(), "stone", 0), /positive safe integer/);
});

test("insufficient inventory cannot craft and does not consume resources", () => {
  const state = addResource(createCraftState(), "stone", 2);
  const result = craft(state, "stone_brick");
  assert.equal(result.ok, false);
  assert.deepEqual(result.missing, { stone: 1 });
  assert.equal(result.state.inventory.stone, 2);
  assert.equal(result.state.artifacts.length, 0);
});

test("stone brick consumes exactly three stone and produces one artifact", () => {
  const state = addResource(createCraftState(), "stone", 4);
  const result = craft(state, "stone_brick");
  assert.equal(result.ok, true);
  assert.equal(result.state.inventory.stone, 1);
  assert.equal(result.artifact.name, "Stone Brick");
  assert.equal(result.state.craftedCount, 1);
});

test("META FORGE CORE requires and consumes one of every resource", () => {
  let state = createCraftState();
  for (const resource of ["stone", "crystal", "gold", "gem"]) {
    state = addResource(state, resource, 1);
  }
  const result = craft(state, "meta_forge_core");
  assert.equal(result.ok, true);
  assert.equal(result.artifact.name, "META FORGE CORE");
  assert.deepEqual(result.state.inventory, { stone: 0, crystal: 0, gold: 0, gem: 0 });
});

test("craft receipt reconciles inventory and artifact ledger", () => {
  let state = addResource(createCraftState(), "gold", 2);
  state = addResource(state, "crystal", 1);
  state = craft(state, "gold_seal").state;
  const receipt = createCraftReceipt(state);
  assert.equal(receipt.craftedCount, 1);
  assert.equal(receipt.artifacts[0].recipeId, "gold_seal");
  assert.equal(receipt.inventory.gold, 0);
  assert.equal(receipt.inventory.crystal, 0);
});

test("unknown recipe is rejected", () => {
  assert.throws(() => canCraft(createCraftState(), "not_a_recipe"), /Unknown recipe/);
});
