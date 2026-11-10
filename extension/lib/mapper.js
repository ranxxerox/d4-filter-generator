(function () {
// Stat/skill mapping - JS port of d4filter/mapper.py (velocity subset:
// exact, abbreviation, normalized-substring and alias matching; the
// difflib fuzzy fallback is replaced by a token-overlap score).
// CommonJS-compatible for node tests.
"use strict";
const core =
  typeof module !== "undefined" && module.exports
    ? require("./core.js")
    : globalThis.D4.core;

const CORE_AFFIXES = new Set([
  "All Damage Multiplier", "Critical Strike Chance", "Critical Strike Damage Multiplier",
  "Attack Speed", "Vulnerable Damage Multiplier", "Fire Damage Multiplier",
  "Shadow Damage Multiplier", "Cold Damage Multiplier", "Lightning Damage Multiplier",
  "Physical Damage Multiplier", "Poison Damage Multiplier", "Holy Damage Multiplier",
  "Damage Over Time Multiplier", "Weapon Damage", "Wrath Regeneration",
  "Mana Regeneration", "Fury Regeneration", "Energy Regeneration", "Essence Regeneration",
  "Spirit Regeneration", "Vigor Regeneration", "Faith Regeneration",
  "Resource Cost Reduction", "Resource Generation",
]);

const ABBREVIATIONS = {
  "crd": "critical strike damage multiplier",
  "chd": "critical strike damage multiplier",
  "crit dmg": "critical strike damage multiplier",
  "crit di": "critical strike damage multiplier",
  "crit chance": "critical strike chance",
  "crit damage": "critical strike damage multiplier",
  "crit strike damage": "critical strike damage multiplier",
  "cs": "critical strike chance",
  "cc": "critical strike chance",
  "ldk": "lucky hit chance",
  "imp ldk": "lucky hit restore primary resource",
  "lucky hit for resource": "lucky hit restore primary resource",
  "lucky hit restore resource": "lucky hit restore primary resource",
  "max life": "maximum life",
  "damage over time": "damage over time multiplier",
  "poison damage": "poison damage multiplier",
  "cold damage": "cold damage multiplier",
  "fire damage": "fire damage multiplier",
  "holy damage": "holy damage multiplier",
  "lightning damage": "lightning damage multiplier",
  "physical damage": "physical damage multiplier",
  "shadow damage": "shadow damage multiplier",
  "vulnerable damage": "vulnerable damage multiplier",
  "resource reduction": "resource cost reduction",
  "critical strike damage": "critical strike damage multiplier",
};

const PROSE_CUES = [
  "stack",
  "temper",
  "look for",
  "prioritise",
  "prioritize",
  "affix",
  "in other slots",
  "roll",
];

const NUMBER_RE = /[\d.]+/g;
const NOISE_CHARS = /[~+%+.!,></:;()"'’]/g;

function normalize(text) {
  return text
    .replace(NOISE_CHARS, " ")
    .replace(NUMBER_RE, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function tokenOverlap(a, b) {
  const at = new Set(a.split(" ").filter(Boolean));
  const bt = new Set(b.split(" ").filter(Boolean));
  if (at.size === 0 || bt.size === 0) return 0;
  let hits = 0;
  for (const t of at) if (bt.has(t)) hits++;
  return hits / Math.max(at.size, bt.size);
}

const DB_BY_LOWER = Object.fromEntries(
  Object.entries(core.DB).map(([name, id]) => [name.toLowerCase(), name])
);

function bestDbMatch(cleaned, aliases) {
  const exact = DB_BY_LOWER[cleaned];
  if (exact) return exact;
  const inSub = Object.keys(DB_BY_LOWER).find((n) => cleaned.includes(n));
  if (inSub && cleaned.length >= 4) return DB_BY_LOWER[inSub];
  const substr = Object.keys(DB_BY_LOWER).filter((n) => n.includes(cleaned));
  if (substr.length) {
    return DB_BY_LOWER[substr.sort((a, b) => b.length - a.length)[0]];
  }
  let best = null, bestScore = 0;
  for (const lower of Object.keys(DB_BY_LOWER)) {
    const score = tokenOverlap(cleaned, lower);
    if (score > bestScore) { best = DB_BY_LOWER[lower]; bestScore = score; }
  }
  return bestScore >= 0.8 ? best : null;
}

function resolveStatLine(line, aliases) {
  const cleaned = normalize(line);
  for (const [phrase, target] of Object.entries(ABBREVIATIONS)) {
    const canonical = DB_BY_LOWER[target];
    if (canonical && new RegExp("\\b" + phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b").test(cleaned)) return canonical;
  }
  const exact = DB_BY_LOWER[cleaned];
  if (exact) return exact;
  const aliasHit = aliases && aliases[line.trim()];
  if (aliasHit && DB_BY_LOWER[aliasHit.toLowerCase()]) return DB_BY_LOWER[aliasHit.toLowerCase()];
  if (cleaned && cleaned.length >= 3) return bestDbMatch(cleaned, aliases);
  return null;
}

function classify(name) {
  return CORE_AFFIXES.has(name) ? "core" : "secondary";
}

function mapStatLines(statLines, aliases) {
  const result = { core: [], secondary: [], skills: [], unmatched: [] };
  for (const line of statLines) {
    const name = resolveStatLine(line, aliases || {});
    if (name) {
      (classify(name) === "core" ? result.core : result.secondary).push(name);
    } else {
      result.unmatched.push(line);
    }
  }
  return result;
}

function mapProse(blob) {
  const result = { core: [], secondary: [], skills: [], unmatched: [] };
  let text = blob.toLowerCase();
  for (const [phrase, target] of Object.entries(ABBREVIATIONS)) {
    text = text.replace(new RegExp("\\b" + phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "g"), target);
  }
  for (const [lower, name] of Object.entries(DB_BY_LOWER)) {
    if (text.includes(lower)) {
      (classify(name) === "core" ? result.core : result.secondary).push(name);
    }
  }
  return result;
}

function mapGuideLines(statLines, aliases) {
  const result = { core: [], secondary: [], skills: [], unmatched: [] };
  for (const line of statLines) {
    let matched = false;
    const name = resolveStatLine(line, aliases || {});
    if (name) {
      (classify(name) === "core" ? result.core : result.secondary).push(name);
      matched = true;
    }
    const prose = mapProse(line);
    if (prose.core.length || prose.secondary.length) {
      result.core.push(...prose.core);
      result.secondary.push(...prose.secondary);
      matched = true;
    }
    if (!matched) result.unmatched.push(line);
  }
  return result;
}

function mapCuratedProse(paragraphs) {
  const kept = paragraphs.filter((p) =>
    PROSE_CUES.some((cue) => new RegExp("\\b" + cue.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b").test(p.toLowerCase()))
  );
  return mapProse(kept.join(" "));
}

const RANK_PHRASE_RE = /ranks?\s+(?:to|of|in)\s+([^,.;!()]+)/gi;

function confirmedSkill(raw) {
  const name = raw.trim().toLowerCase();
  const entry = core.SKILLS.find((s) => s.name.toLowerCase() === name);
  return entry && entry.confirmed ? entry.name : null;
}

function mapRankMentions(lines) {
  const result = { core: [], secondary: [], skills: [], unmatched: [] };
  for (const line of lines) {
    RANK_PHRASE_RE.lastIndex = 0;
    let match;
    while ((match = RANK_PHRASE_RE.exec(line)) !== null) {
      for (const group of match[1].split(/\s+and\s+/)) {
        const parts = group.split("/").map((p) => p.trim()).filter(Boolean);
        if (!parts.length) continue;
        const tail = parts[parts.length - 1].split(/\s+/).pop();
        for (const part of parts) {
          const candidates = [part];
          if (!part.toLowerCase().includes(tail.toLowerCase())) candidates.push(`${part} ${tail}`);
          for (const candidate of candidates) {
            const name = confirmedSkill(candidate);
            if (name) { result.skills.push(name); break; }
          }
        }
      }
    }
  }
  return result;
}

function mapSkills(skillNames) {
  const result = { core: [], secondary: [], skills: [], unmatched: [] };
  for (const raw of skillNames) {
    const name = raw.trim().toLowerCase();
    const entry = core.SKILLS.find((s) => s.name.toLowerCase() === name);
    if (entry) {
      if (entry.confirmed) result.skills.push(entry.name);
    } else {
      result.unmatched.push(raw);
    }
  }
  return result;
}

function generateFromSpec(spec, aliases, goldN, variant) {
  goldN = goldN || 2;
  const tiers =
    typeof module !== "undefined" && module.exports
      ? require("./tiers.js")
      : globalThis.D4.tiers;
  let statLines = spec.statLines || [];
  let skillNames = spec.skills || [];
  if (variant) {
    const payload = (spec.variants || {})[variant];
    if (!payload) throw new Error(`no variant named ${variant}`);
    statLines = payload.statLines || [];
    skillNames = payload.skills || [];
  }
  const statMap = spec.site === "mobalytics"
    ? mapCuratedProse(statLines)
    : mapGuideLines(statLines, aliases || {});
  const skillMap = mapSkills(skillNames);
  const rankMap = mapRankMentions(statLines);

  const uniq = (arr) => [...new Set(arr)];
  const coreStats = uniq(statMap.core);
  const secondary = uniq(statMap.secondary);
  const skills = uniq([...skillMap.skills, ...rankMap.skills]);
  const rankLines = new Set(statLines.filter((line) => mapRankMentions([line]).skills.length));
  const unmatched = uniq([...statMap.unmatched, ...skillMap.unmatched]).filter((line) => !rankLines.has(line));
  const code = tiers.buildRicherFilter(
    spec.title || "My Loot Filter", coreStats, secondary, skills, goldN, spec.gameClass
  );
  return { core: coreStats, secondary, skills, unmatched, code };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    CORE_AFFIXES, normalize, resolveStatLine, classify,
    mapStatLines, mapGuideLines, mapCuratedProse, mapProse, mapRankMentions, mapSkills, generateFromSpec, DB_BY_LOWER,
  };
}
if (typeof globalThis !== "undefined") {
  globalThis.D4 = globalThis.D4 || {};
  globalThis.D4.mapper = {
    CORE_AFFIXES, normalize, resolveStatLine, classify,
    mapStatLines, mapGuideLines, mapCuratedProse, mapProse, mapRankMentions, mapSkills, generateFromSpec, DB_BY_LOWER,
  };
}
})();
