(function () {
// Guide-spec parsers - JS port of d4filter/maxroll.py and mobalytics.py.
// CommonJS-compatible for node tests; the popup calls these on payloads
// forwarded from content scripts.
"use strict";

const STAT_SECTION_HEADINGS = new Set(["important stats", "stats", "stat priority", "stat priorities"]);

function collectEmbedTexts(node, embedType, out) {
  if (Array.isArray(node)) {
    for (const item of node) collectEmbedTexts(item, embedType, out);
  } else if (node && typeof node === "object") {
    if (node.embedType === embedType && typeof node.text === "string") {
      out.push(node.text);
    }
    for (const value of Object.values(node)) collectEmbedTexts(value, embedType, out);
  }
}

function findImportantStats(root) {
  const lines = [];
  const joinParts = (node) => {
    const parts = [];
    if (Array.isArray(node)) {
      for (const item of node) parts.push(joinParts(item));
    } else if (node && typeof node === "object") {
      if (typeof node.text === "string") parts.push(node.text);
      for (const value of Object.values(node)) parts.push(joinParts(value));
    }
    return parts.filter(Boolean).join(" ").trim();
  };
  const walk = (node) => {
    if (Array.isArray(node)) {
      for (const item of node) walk(item);
    } else if (node && typeof node === "object") {
      const children = node.children;
      if (Array.isArray(children)) {
        children.forEach((child, index) => {
          const texts = (child && Array.isArray(child.children) ? child.children : [])
            .map((c) => (c && typeof c.text === "string" ? c.text : ""));
          if (texts.some((t) => STAT_SECTION_HEADINGS.has(t.trim().toLowerCase()))) {
            const payload = index + 1 < children.length ? children[index + 1] : null;
            const bullets = payload && Array.isArray(payload.children) ? payload.children : [];
            for (const bullet of bullets) {
              const line = joinParts(bullet);
              if (line) lines.push(line);
            }
          }
          walk(child);
        });
      }
      for (const value of Object.values(node)) walk(value);
    }
  };
  walk(root);
  return lines;
}

function parseMaxrollContext(context, sourceUrl) {
  const loader = (context.state || {}).loaderData || {};
  let post = null;
  for (const value of Object.values(loader)) {
    if (value && typeof value === "object" && value.post) {
      post = value.post;
      break;
    }
  }
  if (!post) throw new Error("no post payload in maxroll remix context");

  const spec = {
    site: "maxroll",
    sourceUrl: sourceUrl || "",
    title: post.title || "",
    gameClass: "",
    season: null,
    profileNames: [],
    skills: [],
    skillIds: [],
    variants: {},
    affixMentions: [],
    statLines: [],
    guideFilterCodes: [],
  };

  for (const block of post.gutenbergBlock || []) {
    const profile = block.plannerProfile;
    if (!profile) continue;
    const data = profile.data || {};
    if (!spec.gameClass) {
      spec.gameClass = profile.class || "";
      const season = parseInt(data.season, 10);
      spec.season = Number.isNaN(season) ? null : season;
    }
    if (spec.season === null) {
      for (const tag of post.tags || []) {
        const match = /Season\s+(\d+)/.exec((tag && tag.name) || "");
        if (match) { spec.season = parseInt(match[1], 10); break; }
      }
    }
    const profiles = data.profiles || [];
    spec.profileNames = profiles.map((p) => p.name || "");

    const skills = [];
    const affixes = [];
    for (const prof of profiles) {
      const notes = prof.widgetNotes || {};
      const profSkills = [];
      collectEmbedTexts(notes, "d4-skill", profSkills);
      collectEmbedTexts(notes, "d4-affix", affixes);
      const profStats = findImportantStats(notes);
      skills.push(...profSkills);
      spec.statLines.push(...profStats);
      spec.variants[prof.name || ""] = {
        statLines: [...new Set(profStats)],
        skills: [...new Set(profSkills)],
      };
      for (const line of prof.skillBar || []) {
        if (typeof line === "string") spec.skillIds.push(line);
      }
    }
    spec.skills = [...new Set(skills)];
    spec.affixMentions = [...new Set(affixes)].sort();
    spec.statLines = [...new Set(spec.statLines)];

    for (const loot of data.lootFilters || []) {
      if (loot.code) spec.guideFilterCodes.push([loot.name || "", loot.code]);
    }
  }
  return spec;
}

function blobFromLexical(node) {
  const parts = [];
  if (Array.isArray(node)) {
    for (const item of node) parts.push(blobFromLexical(item));
  } else if (node && typeof node === "object") {
    if (node.type === "static-data-widget") {
      parts.push(node.label || node.text || "");
    } else if (typeof node.text === "string") {
      parts.push(node.text);
    }
    for (const value of Object.values(node)) parts.push(blobFromLexical(value));
  }
  return parts.filter(Boolean).join(" ").trim();
}

function skillLabels(doc) {
  const labels = [];
  const walk = (node) => {
    if (Array.isArray(node)) {
      for (const item of node) walk(item);
    } else if (node && typeof node === "object") {
      if (
        node.type === "static-data-widget" &&
        node.groupId === "skills" &&
        typeof node.label === "string"
      ) {
        labels.push(node.label.split(":")[0].trim());
      }
      for (const value of Object.values(node)) walk(value);
    }
  };
  walk(doc);
  return [...new Set(labels)];
}

function blockTexts(root) {
  const blocks = [];
  const collect = (node) => {
    if (Array.isArray(node)) {
      for (const item of node) collect(item);
      return;
    }
    if (!node || typeof node !== "object") return;
    const kind = node.type;
    if (kind === "paragraph" || kind === "listitem") {
      const text = (node.children || [])
        .map((child) => blobFromLexical(child))
        .filter(Boolean)
        .join(" ")
        .split(/\s+/)
        .filter(Boolean)
        .join(" ");
      if (text) blocks.push(text);
      return;
    }
    if (kind === "list") {
      for (const child of node.children || []) collect(child);
      return;
    }
    for (const value of Object.values(node)) collect(value);
  };
  collect(root);
  return blocks;
}

function statProse(doc) {
  const paragraphs = [];
  for (const node of doc.content || []) {
    const content = node.data || {};
    const simplified = content.simplifiedContent || {};
    const root = (simplified.value || {}).root;
    if (root) paragraphs.push(...blockTexts(root));
  }
  return [...new Set(paragraphs.filter((p) => p.trim()))];
}

function parseMobalyticsState(state, sourceUrl) {

  let doc = null;
  const queries = ((state.diablo4State || {}).apollo || {}).graphqlV2?.queries || [];
  for (const model of queries) {
    const data = (model.state || {}).data;
    if (!Array.isArray(data)) continue;
    for (const entry of data) {
      if (!entry || typeof entry !== "object") continue;
      const build = (((entry.game || {}).documents || {}).userGeneratedDocumentBySlug) || {};
      if (build.data && build.data.content) {
        doc = build.data;
        break;
      }
    }
    if (doc) break;
  }
  if (!doc) throw new Error("no build document in mobalytics preloaded state");

  const tagValue = (groupSlug) => {
    for (const tag of ((doc.tags || {}).data || [])) {
      if (tag && tag.groupSlug === groupSlug) return tag.name;
    }
    return null;
  };

  const seasonName = tagValue("season");
  return {
    site: "mobalytics",
    sourceUrl: sourceUrl || "",
    title: (doc.data && doc.data.name) || doc.slugifiedName || "",
    gameClass: tagValue("class") || "",
    season: seasonName ? parseInt(String(seasonName).replace("Season", "").trim(), 10) || null : null,
    profileNames: [],
    skills: skillLabels(doc),
    skillIds: [],
    affixMentions: [],
    statLines: statProse(doc),
    guideFilterCodes: [],
  };
}

  function parseMaxroll(htmlOrContext, sourceUrl) {
    if (htmlOrContext && typeof htmlOrContext === "object") {
      return parseMaxrollContext(htmlOrContext, sourceUrl);
    }
    const match = String(htmlOrContext).match(
      /window\.__remixContext\s*=\s*(\{[\s\S]*?\});?\s*<\/script>/
    );
    if (!match) throw new Error("no window.__remixContext found");
    return parseMaxrollContext(JSON.parse(match[1]), sourceUrl);
  }

  function parseMobalytics(htmlOrState, sourceUrl) {
    if (htmlOrState && typeof htmlOrState === "object") {
      return parseMobalyticsState(htmlOrState, sourceUrl);
    }
    const match = String(htmlOrState).match(
      /window\.__PRELOADED_STATE__\s*=\s*(\{[\s\S]*?\});?\s*<\/script>/
    );
    if (!match) throw new Error("no window.__PRELOADED_STATE__ found");
    return parseMobalyticsState(JSON.parse(match[1].replace(/;\s*$/, "")), sourceUrl);
  }

if (typeof module !== "undefined" && module.exports) {
  module.exports = { parseMaxroll, parseMobalytics };
}
if (typeof globalThis !== "undefined") {
  globalThis.D4 = globalThis.D4 || {};
  globalThis.D4.parsers = { parseMaxroll, parseMobalytics };
}
})();
