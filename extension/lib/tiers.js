(function () {
// Richer filter tier builder - JS port of d4filter/rules.py.
// CommonJS-compatible for node tests; loaded by the popup.
"use strict";
const core =
  typeof module !== "undefined" && module.exports
    ? require("./core.js")
    : globalThis.D4.core;

const VIOLET = core.makeColor(155, 89, 182);

const CLASS_RESOURCE = {
  Barbarian: "Fury",
  Druid: "Spirit",
  Necromancer: "Essence",
  Rogue: "Energy",
  Sorcerer: "Mana",
  Warlock: "Wrath",
  Spiritborn: "Vigor",
  Paladin: "Faith",
};

function hideDeadAffixes(gameClass) {
  const own = CLASS_RESOURCE[gameClass];
  if (!own) return [];
  const deadPrefixes = new Set(
    Object.values(CLASS_RESOURCE).filter((r) => r !== own)
  );
  const dead = [];
  for (const [name] of Object.entries(core.DB)) {
    if (
      (name.includes("Regeneration") || name.includes("On Kill") || name.includes("every 10 Kills")) &&
      [...deadPrefixes].some((p) => name.startsWith(p + " "))
    ) {
      dead.push(name);
    }
  }
  return dead;
}

function buildRicherFilter(name, coreStats, secondary, skills, goldN, gameClass) {
  goldN = goldN || 2;
  const uniq = (arr) => [...new Set(arr)];
  const coreIds = uniq(coreStats.filter((n) => n in core.DB).map((n) => core.DB[n]));
  const secIds = uniq(secondary.filter((n) => n in core.DB).map((n) => core.DB[n]));
  const skillIds = uniq(
    skills
      .map((n) => core.SKILLS.find((s) => s.name === n && s.confirmed && s.id))
      .filter(Boolean)
      .map((s) => s.id)
  );

  const allGood = [...coreIds, ...secIds, ...skillIds];

  const rules = [
    core.makeRule("Legendary Talismans", core.SHOW, [
      core.condRarity(core.LEG_PLUS),
      core.condTypes([core.CHARM, core.SEAL]),
    ]),
    core.makeRule("Hide Junk", core.HIDE_ALL, [
      core.condRarity(core.COMMON | core.MAGIC | core.RARE),
    ]),
  ];

  if (allGood.length > 0) {
    rules.push(
      core.makeRule(
        "Check Rare - Build Affix",
        core.RECOLOR,
        [core.condRarity(core.RARE), core.condAffixes(allGood, 1)],
        core.C_ORANGE
      )
    );
  }

  if (gameClass && CLASS_RESOURCE[gameClass]) {
    const dead = hideDeadAffixes(gameClass);
    if (dead.length > 0) {
      rules.push(
        core.makeRule(
          "Hide Other-Class Resource",
          core.HIDE_ALL,
          [
            core.condRarity(core.RARE),
            core.condAffixes(dead.map((d) => core.DB[d]).filter(Boolean), 1),
          ]
        )
      );
    }
  }

  const nearN = Math.max(1, goldN - 1);
  if (coreIds.length >= nearN) {
    rules.push(
      core.makeRule(
        `Near BiS - ${nearN}+ Core Stats`,
        core.RECOLOR,
        [core.condRarity(core.RARE), core.condAffixes(coreIds, nearN)],
        VIOLET
      )
    );
  }

  if (coreIds.length >= goldN) {
    rules.push(
      core.makeRule(
        `BiS Rare - ${goldN}+ Dmg Stats`,
        core.RECOLOR,
        [core.condRarity(core.RARE), core.condAffixes(coreIds, goldN)],
        core.C_GOLD
      )
    );
  }

  rules.push(
    core.makeRule("Codex Upgrade", core.RECOLOR, [core.condCodex()], core.C_GREEN)
  );
  rules.push(
    core.makeRule("Legendaries - Keep All", core.RECOLOR, [core.condRarity(core.LEG_PLUS)], core.C_GREEN)
  );
  rules.push(
    core.makeRule("Greater Affix - Loot", core.RECOLOR, [core.condGreaterAffix(1)], core.C_CYAN)
  );
  rules.push(
    core.makeRule("Show All - Catch All", core.SHOW, [core.condRarity(core.ALL_RAR)])
  );

  return core.toBase64(core.makeFilter(name, rules));
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { buildRicherFilter, hideDeadAffixes, CLASS_RESOURCE, VIOLET };
}
if (typeof globalThis !== "undefined") {
  globalThis.D4 = globalThis.D4 || {};
  globalThis.D4.tiers = { buildRicherFilter, hideDeadAffixes, CLASS_RESOURCE, VIOLET };
}
})();
