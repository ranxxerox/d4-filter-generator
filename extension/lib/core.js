// GENERATED FILE - do not edit by hand.
// Regenerate with: python3 tools/sync_extension_data.py
// Source: index.html script block (data tables + protobuf encoder).
// CommonJS-compatible so node tests can require() it and the extension
// can load it via a classic <script> tag.

const DB = {
  // Offensive
  "Weapon Damage":                       0x0027fc93,
  "Strength":                            0x001beac2,
  "Intelligence":                        0x001beabe,
  "Willpower":                           0x001beab4,
  "Dexterity":                           0x001beaba,
  "Thorns":                              0x001beb22,
  "All Damage Multiplier":               0x001beac6,
  "Attack Speed":                        0x001beace,
  "Critical Strike Chance":              0x001bead2,
  "Critical Strike Damage Multiplier":   0x001bead4,
  "Vulnerable Damage Multiplier":        0x001bfc80,
  "Damage Over Time Multiplier":         0x001bead6,
  "Cold Damage Multiplier":              0x00270af5,
  "Fire Damage Multiplier":              0x00270af7,
  "Holy Damage Multiplier":              0x00270aff,
  "Lightning Damage Multiplier":         0x00270afd,
  "Physical Damage Multiplier":          0x00270ad0,
  "Poison Damage Multiplier":            0x00270afb,
  "Shadow Damage Multiplier":            0x00270af9,
  // Defensive
  "Maximum Life":                        0x001bead8,
  "Life Regeneration":                   0x001beada,
  "Life On Hit":                         0x001d5e13,
  "Life on Kill":                        0x0025da8c,
  "Armor":                               0x001beab2,
  "Resistance to All Elements":          0x001bfd38,
  "Fire Resistance":                     0x001beaee,
  "Cold Resistance":                     0x001beb2e,
  "Lightning Resistance":                0x001beaf2,
  "Poison Resistance":                   0x001beaf4,
  "Shadow Resistance":                   0x001beaf6,
  "Physical Resistance":                 0x002557e4,
  "Damage Reduction":                    0x001d6e63,
  "Dodge Chance":                        0x001bfc85,
  // Resource
  "Maximum Resource":                    0x001bfc79,
  "Energy Regeneration":                 0x001d5e30,
  "Essence Regeneration":                0x001d5e3a,
  "Fury Regeneration":                   0x001d5e38,
  "Mana Regeneration":                   0x001d5e36,
  "Spirit Regeneration":                 0x001d5e33,
  "Vigor Regeneration":                  0x001eb549,
  "Faith Regeneration":                  0x002674b9,
  "Wrath Regeneration":                  0x0026a37c,
  "Energy On Kill":                      0x001d5e25,
  "Essence On Kill":                     0x001d5e27,
  "Fury On Kill":                        0x001d5e29,
  "Mana On Kill":                        0x001d5e2b,
  "Spirit On Kill":                      0x001d5e2d,
  "Vigor On Kill":                       0x001eb481,
  "Faith On Kill":                       0x002674bb,
  "Wrath every 10 Kills":               0x0026a374,
  "Resource Cost Reduction":             0x001d3a0f,
  "Resource Generation":                 0x001beb20,
  "Lucky Hit Restore Primary Resource": 0x0024527f,
  // Utility
  "Potion Capacity":                     0x001beae2,
  "Lucky Hit Chance":                    0x001beadc,
  "Healing Received":                    0x001bfcbf,
  "Fortify Generation":                  0x00266b1e,
  "Barrier Generation":                  0x00266b22,
  // Mobility
  "Movement Speed":                      0x001beade,
  "Attacks Reduce Evade Cooldown":       0x0026c56c,
  "Maximum Evade Charge":                0x0026c56e,
  "Evade Grants Movement Speed":         0x0026c570,
};

// Skill ranks — Warlock confirmed, others pending
const SKILLS = [
  // Warlock (confirmed)
  { name: "Hell Fracture",       id: 0x00273c0a, class: "Warlock",    confirmed: true },
  { name: "Abyss Skills",        id: 0x0026ad42, class: "Warlock",    confirmed: true },
  { name: "Hellfire Skills",     id: 0x0026adc4, class: "Warlock",    confirmed: true },
  { name: "Occult Skills",       id: 0x0026adc6, class: "Warlock",    confirmed: true },
  { name: "Demonology Skills",   id: 0x0026adcd, class: "Warlock",    confirmed: true },
  { name: "Sigil of Chaos",      id: 0x0026adc2, class: "Warlock",    confirmed: true },
  { name: "Sigil of Summons",    id: 0x0026adc8, class: "Warlock",    confirmed: true },
  { name: "Sigil of Subversion", id: 0x0026ad87, class: "Warlock",    confirmed: true },
  { name: "Blazing Scream",      id: 0x0026ad89, class: "Warlock",    confirmed: true },
  { name: "Bombardment",         id: 0x0026ad8b, class: "Warlock",    confirmed: true },
  { name: "Rampage",             id: 0x0026ad7e, class: "Warlock",    confirmed: true },
  { name: "Tyrant's Grasp",      id: 0x0026ad46, class: "Warlock",    confirmed: true },
  { name: "Dread Claws",         id: 0x0026ad48, class: "Warlock",    confirmed: true },
  // Generic (confirmed)
  { name: "Core Skills",         id: 0x001d6e31, class: "All",        confirmed: true },
  { name: "All Skills",          id: 0x0026ad83, class: "All",        confirmed: true },
  // Other classes — IDs pending (shown as reference, not selectable yet)
  { name: "Bash",                id: null, class: "Barbarian",  confirmed: false },
  { name: "Whirlwind",           id: null, class: "Barbarian",  confirmed: false },
  { name: "Hammer of the Ancients", id: null, class: "Barbarian", confirmed: false },
  { name: "Leap",                id: null, class: "Barbarian",  confirmed: false },
  { name: "Rend",                id: null, class: "Barbarian",  confirmed: false },
  { name: "Weapon Mastery Skills", id: null, class: "Barbarian", confirmed: false },
  { name: "Landslide",           id: null, class: "Druid",      confirmed: false },
  { name: "Tornado",             id: null, class: "Druid",      confirmed: false },
  { name: "Pulverize",           id: null, class: "Druid",      confirmed: false },
  { name: "Shred",               id: null, class: "Druid",      confirmed: false },
  { name: "Wolves",              id: null, class: "Druid",      confirmed: false },
  { name: "Bone Spear",          id: null, class: "Necromancer", confirmed: false },
  { name: "Blood Surge",         id: null, class: "Necromancer", confirmed: false },
  { name: "Corpse Explosion",    id: null, class: "Necromancer", confirmed: false },
  { name: "Bone Skills",         id: null, class: "Necromancer", confirmed: false },
  { name: "Blood Skills",        id: null, class: "Necromancer", confirmed: false },
  { name: "Twisting Blades",     id: null, class: "Rogue",      confirmed: false },
  { name: "Rapid Fire",          id: null, class: "Rogue",      confirmed: false },
  { name: "Penetrating Shot",    id: null, class: "Rogue",      confirmed: false },
  { name: "Marksman Skills",     id: null, class: "Rogue",      confirmed: false },
  { name: "Cutthroat Skills",    id: null, class: "Rogue",      confirmed: false },
  { name: "Fireball",            id: null, class: "Sorcerer",   confirmed: false },
  { name: "Ice Shards",          id: null, class: "Sorcerer",   confirmed: false },
  { name: "Chain Lightning",     id: null, class: "Sorcerer",   confirmed: false },
  { name: "Blizzard",            id: null, class: "Sorcerer",   confirmed: false },
  { name: "Frost Skills",        id: null, class: "Sorcerer",   confirmed: false },
  { name: "Pyromancy Skills",    id: null, class: "Sorcerer",   confirmed: false },
  { name: "Shock Skills",        id: null, class: "Sorcerer",   confirmed: false },
  { name: "Quill Volley",        id: null, class: "Spiritborn", confirmed: false },
  { name: "Soar",                id: null, class: "Spiritborn", confirmed: false },
  { name: "Thunderspike",        id: null, class: "Spiritborn", confirmed: false },
  { name: "Eagle Skills",        id: null, class: "Spiritborn", confirmed: false },
  { name: "Jaguar Skills",       id: null, class: "Spiritborn", confirmed: false },
];

// ── Affix categories for UI ───────────────────────────────────
const CORE_CANDIDATES = [
  { group: "Offensive — Damage", affixes: [
    "All Damage Multiplier","Critical Strike Chance","Critical Strike Damage Multiplier",
    "Attack Speed","Vulnerable Damage Multiplier","Fire Damage Multiplier",
    "Shadow Damage Multiplier","Cold Damage Multiplier","Lightning Damage Multiplier",
    "Physical Damage Multiplier","Poison Damage Multiplier","Holy Damage Multiplier",
    "Damage Over Time Multiplier","Weapon Damage",
  ]},
  { group: "Offensive — Primary Stats", affixes: [
    "Strength","Intelligence","Willpower","Dexterity",
  ]},
  { group: "Resource", affixes: [
    "Wrath Regeneration","Mana Regeneration","Fury Regeneration","Energy Regeneration",
    "Essence Regeneration","Spirit Regeneration","Vigor Regeneration","Faith Regeneration",
    "Resource Cost Reduction","Resource Generation",
  ]},
  { group: "Defensive", affixes: [
    "Maximum Life","Armor","Damage Reduction","Dodge Chance",
    "Resistance to All Elements","Fire Resistance","Cold Resistance",
    "Lightning Resistance","Poison Resistance","Shadow Resistance","Physical Resistance",
    "Life Regeneration","Life On Hit","Life on Kill",
  ]},
  { group: "Utility", affixes: [
    "Lucky Hit Chance","Lucky Hit Restore Primary Resource","Healing Received",
    "Barrier Generation","Fortify Generation","Potion Capacity",
  ]},
  { group: "Mobility", affixes: [
    "Movement Speed","Maximum Evade Charge","Attacks Reduce Evade Cooldown",
    "Evade Grants Movement Speed",
  ]},
];

// ── State ─────────────────────────────────────────────────────
const state = {
  coreStats: new Set(),
  secondaryStats: new Set(),
  skills: new Set(),
  lastCode: "",
};

// ── Presets ───────────────────────────────────────────────────
const PRESETS = {
  "hf-warlock": {
    filterName: "HF Warlock",
    class: "Warlock",
    core: ["Critical Strike Chance","Critical Strike Damage Multiplier","Attack Speed",
           "All Damage Multiplier","Vulnerable Damage Multiplier","Fire Damage Multiplier",
           "Shadow Damage Multiplier","Wrath Regeneration"],
    secondary: ["Willpower","Maximum Life"],
    skills: ["Hell Fracture","Abyss Skills","Core Skills","All Skills",
             "Hellfire Skills","Occult Skills","Sigil of Chaos","Sigil of Summons",
             "Sigil of Subversion","Blazing Scream","Bombardment","Rampage"],
  },
  "generic-crit": {
    filterName: "Generic Crit",
    class: "all",
    core: ["Critical Strike Chance","Critical Strike Damage Multiplier","Attack Speed",
           "All Damage Multiplier","Vulnerable Damage Multiplier"],
    secondary: ["Maximum Life","Armor"],
    skills: ["Core Skills","All Skills"],
  },
  "clear": {
    filterName: "My Loot Filter",
    class: "all",
    core: [], secondary: [], skills: [],
  },
};

// ════════════════════════════════════════════════════════════
// PROTOBUF ENCODER
// ════════════════════════════════════════════════════════════
function encodeVarint(value) {
  const bytes = [];
  while (true) {
    bytes.push(value & 0x7F);
    value = Math.floor(value / 128);
    if (value === 0) break;
  }
  for (let i = 0; i < bytes.length - 1; i++) bytes[i] |= 0x80;
  return new Uint8Array(bytes);
}
function efv(fn, v) {
  return concat(encodeVarint((fn << 3) | 0), encodeVarint(v));
}
function ef32(fn, v) {
  const buf = new Uint8Array(5);
  buf.set(encodeVarint((fn << 3) | 5));
  new DataView(buf.buffer).setUint32(1, v, true);
  return buf;
}
function efb(fn, data) {
  return concat(encodeVarint((fn << 3) | 2), encodeVarint(data.length), data);
}
function efs(fn, str) {
  return efb(fn, new TextEncoder().encode(str));
}
function concat(...arrays) {
  const len = arrays.reduce((a, b) => a + b.length, 0);
  const out = new Uint8Array(len);
  let pos = 0;
  for (const arr of arrays) { out.set(arr, pos); pos += arr.length; }
  return out;
}

function condRarity(mask)      { return efb(4, concat(efv(1,1), efv(4,mask))); }
function condGreaterAffix(n)   { return efb(4, concat(efv(1,3), efv(6,n))); }
function condCodex()           { return efb(4, concat(efv(1,4), efv(4,1), efv(6,1))); }
function condAffixes(ids, n)   {
  let inner = efv(1,6);
  for (const id of ids) inner = concat(inner, ef32(2, id));
  inner = concat(inner, efv(4, n));
  return efb(4, inner);
}
function condTypes(ids) {
  let inner = efv(1,5);
  for (const id of ids) inner = concat(inner, ef32(2, id));
  return efb(4, inner);
}

const SHOW=0, RECOLOR=2, HIDE_ALL=3;
const COMMON=0x01,MAGIC=0x02,RARE=0x04,LEGENDARY=0x08,UNIQUE=0x10,MYTHIC=0x20,TALISMAN=0x40;
const LEG_PLUS = LEGENDARY|UNIQUE|MYTHIC|TALISMAN;
const ALL_RAR  = 0x7F;

function makeColor(r,g,b,a=255) { return ((a<<24)|(b<<16)|(g<<8)|r) >>> 0; }
const C_CYAN   = makeColor(0,255,255);
const C_GREEN  = makeColor(0,200,0);
const C_ORANGE = makeColor(255,140,0);
const C_GOLD   = makeColor(255,215,0);
const C_DEF    = 0xFFFF0000;
const CHARM    = 0x00237e80;
const SEAL     = 0x0022ed05;

function makeRule(name, vis, conds, color=C_DEF) {
  let r = concat(efs(1,name), efv(2,vis), ef32(3,color));
  for (const c of conds) r = concat(r, c);
  r = concat(r, efv(5,1));
  return efb(1, r);
}
function makeFilter(name, rules) {
  let d = new Uint8Array(0);
  for (const r of rules) d = concat(d, r);
  d = concat(d, efs(2,name), efv(3,rules.length), efv(4,1));
  return d;
}

function toBase64(bytes) {
  let binary = '';
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    DB, SKILLS, state, PRESETS,
    encodeVarint, efv, ef32, efb, efs, concat,
    condRarity, condGreaterAffix, condCodex, condAffixes, condTypes,
    SHOW, RECOLOR, HIDE_ALL, COMMON, MAGIC, RARE, LEGENDARY, UNIQUE,
    MYTHIC, TALISMAN, LEG_PLUS, ALL_RAR, makeColor,
    C_CYAN, C_GREEN, C_ORANGE, C_GOLD, C_DEF, CHARM, SEAL,
    makeRule, makeFilter, toBase64,
  };
}
if (typeof globalThis !== "undefined") {
  globalThis.D4 = globalThis.D4 || {};
  globalThis.D4.core = {
    DB, SKILLS, state, PRESETS,
    encodeVarint, efv, ef32, efb, efs, concat,
    condRarity, condGreaterAffix, condCodex, condAffixes, condTypes,
    SHOW, RECOLOR, HIDE_ALL, COMMON, MAGIC, RARE, LEGENDARY, UNIQUE,
    MYTHIC, TALISMAN, LEG_PLUS, ALL_RAR, makeColor,
    C_CYAN, C_GREEN, C_ORANGE, C_GOLD, C_DEF, CHARM, SEAL,
    makeRule, makeFilter, toBase64,
  };
}
