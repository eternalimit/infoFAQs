/**
 * CAT BOT — Mine the Craft: browser-independent crafting engine core.
 * Pure state transitions; no network, wallet, storage, or blockchain dependency.
 */
export const RESOURCE_KEYS = Object.freeze(["stone", "crystal", "gold", "gem"]);

export const RECIPES = Object.freeze({
  stone_brick: Object.freeze({
    name: "Stone Brick",
    costs: Object.freeze({ stone: 3 }),
    description: "A basic construction artifact."
  }),
  crystal_lens: Object.freeze({
    name: "Crystal Lens",
    costs: Object.freeze({ crystal: 2, stone: 1 }),
    description: "A precision crafting component."
  }),
  gold_seal: Object.freeze({
    name: "Gold Seal",
    costs: Object.freeze({ gold: 2, crystal: 1 }),
    description: "A marked metal artifact."
  }),
  meta_forge_core: Object.freeze({
    name: "META FORGE CORE",
    costs: Object.freeze({ stone: 1, crystal: 1, gold: 1, gem: 1 }),
    description: "One of each mined resource; the core craft artifact."
  })
});

const RESOURCE_NAMES = Object.freeze({
  stone: "Stone",
  crystal: "Crystal",
  gold: "Gold",
  gem: "Gem"
});

function positiveInteger(value, label) {
  if (!Number.isSafeInteger(value) || value <= 0) {
    throw new TypeError(label + " must be a positive safe integer.");
  }
  return value;
}

function normalizeResource(resource) {
  const key = String(resource).toLowerCase();
  if (!RESOURCE_KEYS.includes(key)) {
    throw new RangeError("Unknown resource: " + resource);
  }
  return key;
}

export function createCraftState() {
  return {
    version: 1,
    inventory: { stone: 0, crystal: 0, gold: 0, gem: 0 },
    artifacts: [],
    craftedCount: 0
  };
}

export function addResource(state, resource, quantity = 1) {
  assertCraftState(state);
  const key = normalizeResource(resource);
  positiveInteger(quantity, "quantity");
  const next = structuredClone(state);
  next.inventory[key] += quantity;
  if (!Number.isSafeInteger(next.inventory[key])) {
    throw new RangeError("Inventory limit exceeded.");
  }
  return next;
}

export function canCraft(state, recipeId) {
  assertCraftState(state);
  const recipe = RECIPES[recipeId];
  if (!recipe) throw new RangeError("Unknown recipe: " + recipeId);
  const missing = {};
  for (const [resource, required] of Object.entries(recipe.costs)) {
    const shortfall = required - state.inventory[resource];
    if (shortfall > 0) missing[resource] = shortfall;
  }
  return { ok: Object.keys(missing).length === 0, missing };
}

export function craft(state, recipeId) {
  const availability = canCraft(state, recipeId);
  if (!availability.ok) {
    return { ok: false, state, missing: availability.missing, artifact: null };
  }
  const recipe = RECIPES[recipeId];
  const next = structuredClone(state);
  for (const [resource, required] of Object.entries(recipe.costs)) {
    next.inventory[resource] -= required;
  }
  next.craftedCount += 1;
  const artifact = {
    id: "artifact-" + String(next.craftedCount).padStart(6, "0"),
    recipeId,
    name: recipe.name,
    description: recipe.description,
    costs: { ...recipe.costs },
    craftedOrdinal: next.craftedCount
  };
  next.artifacts.push(artifact);
  assertCraftState(next);
  return { ok: true, state: next, missing: {}, artifact };
}

export function assertCraftState(state) {
  if (!state || state.version !== 1 || !state.inventory || !Array.isArray(state.artifacts)) {
    throw new TypeError("Invalid crafting state.");
  }
  for (const key of RESOURCE_KEYS) {
    if (!Number.isSafeInteger(state.inventory[key]) || state.inventory[key] < 0) {
      throw new TypeError("Invalid inventory quantity for " + key + ".");
    }
  }
  if (!Number.isSafeInteger(state.craftedCount) || state.craftedCount !== state.artifacts.length) {
    throw new TypeError("Crafted artifact count does not reconcile.");
  }
  return true;
}

export function createCraftReceipt(state) {
  assertCraftState(state);
  return {
    engine: "CAT BOT Mine the Craft",
    engineVersion: "1.0.0",
    inventory: { ...state.inventory },
    artifacts: state.artifacts.map(item => ({ ...item, costs: { ...item.costs } })),
    craftedCount: state.craftedCount
  };
}

export function resourceDisplayName(resource) {
  return RESOURCE_NAMES[normalizeResource(resource)];
}
