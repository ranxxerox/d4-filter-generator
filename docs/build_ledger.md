# d4-filter-generator Build Ledger

Initialized: 2026-10-09

## Current Factory State

```text
status: running / product slices complete, hardening backlog open
work_mode: velocity
role_topology: lean_solo
user_involvement: hands_off
feedback_handling: no_manager
principal_policy: none
principal_authority: observe
principal_intervention_policy: no_baton_interference
config_verbosity: compact
target_outcome: d4filter CLI: scrape maxroll/mobalytics build guides and emit D4 loot filter import codes
goal_policy: none
acceptance_tier: integration
factory_topology: executive_as_ledger
reviewer_policy: risk_triggered
reviewer_spawn_policy: after_handoff
manager_policy: none
thread_cleanup_policy: none
cleanup_keep_recent: 3
factory_stop_policy: enabled
default_stop_mode: drain_to_checkpoint
stop_scope: all_factory
stop_authority: principal_or_user
stop_monitor_policy: pause_after_stop
stop_cleanup_policy: rolling_window_after_checkpoint
resume_policy: resume_from_stop_packet
default_resume_mode: continue_same_baton
stop_packet_required: true
stop_state: running
last_stop_packet: none
permission_profile: full_access
sandbox_mode: full_access
approval_policy: on_failure
tool_call_budget_policy: bounded_reads
thread_read_policy: latest_only
active_actor_polling_policy: adaptive_backoff
active_builder_poll_interval: 3m
long_check_poll_interval: 5m
handoff_poll_interval: 60s
stale_ping_after: 10m_without_meaningful_progress
stale_reclaim_after: 20m_to_30m_policy_dependent
model_switch_policy: by_role
capability_preflight: minimal
active_writer:
active_reviewer:
principal_thread:
manager_thread:
current_baton: B-007
last_accepted_baton: B-007
last_release_gate: none
remote_status:
```

## Active Threads

| Role | Thread | Status | Scope | Notes |
| --- | --- | --- | --- | --- |

## Thread Cleanup

| Policy | Keep Recent | Last Cleanup | Notes |
| --- | --- | --- | --- |
| none | 3 | none | Preserve active, unresolved, pinned, Executive, Ledger, and Manager threads |

## Stop And Resume

| State | Default Stop | Scope | Authority | Monitor Policy | Cleanup Policy | Resume Policy | Default Resume |
| --- | --- | --- | --- | --- | --- | --- | --- |
| running | drain_to_checkpoint | all_factory | principal_or_user | pause_after_stop | rolling_window_after_checkpoint | resume_from_stop_packet | continue_same_baton |

Latest stop packet: none
Latest resume packet: none

## Capability Preflight

| Capability | Status | Evidence | Blocker policy |
| --- | --- | --- | --- |
| thread tools | absent | Crush runtime has no delegated-worker/thread tooling | manual single-writer factory; lean_solo confirmed; Executive thread acts as active writer |
| thread tool schema | n/a |  | thread tools absent |
| thread read policy support | n/a |  | thread tools absent |
| tool call limits | n/a |  | thread tools absent |
| automations | absent | no heartbeat/automation tooling in Crush | doc-based checkpoint instead |
| goal tooling | n/a |  | goal_policy=none |
| git write | available | clean worktree, local repo, commits permitted per_vertical_slice | dirty=pause_reconcile |
| push auth | unknown | push=local_only; keep local commit on auth failure | git_auth=local_commit_continue |
| browser | none | fetch/httpx for guide retrieval; no browser QA planned | browser QA off (velocity) |
| package manager | available | python3 3.14.7 venv + pip; node v26.10.0 for golden encoder harness | long_tests=focused_then_checkpoint |
| tests | installable | pytest missing from system python; create project venv | flakes=rerun_once |
| env/secrets | none needed | no fetch-time creds; guide fetching is public | credentials=use_existing_only |

## Effective Config Summary

```text
mode/topology: velocity / lean_solo / executive_as_ledger
target/tier: d4filter CLI: scrape maxroll/mobalytics build guides and emit D4 loot filter import codes / integration
principal: hands_off; policy=none; authority=observe; intervention=no_baton_interference
feedback: no_manager; manager=none; executive_context=direct_user_chat
model routing: by_role; principal=user-preferred capable model/high; executive=user-preferred capable model/high; ledger=user-preferred capable model/high; builder=user-preferred capable model/high; reviewer=user-preferred capable model/high; manager=user-preferred capable model/high; watcher=user-preferred capable model/high; fallback=user-preferred capable model/high
permission: full_access; sandbox=full_access; approval=on_failure
tool-call/thread-read: bounded_reads / latest_only
active polling: adaptive_backoff; builder=3m; long_check=5m; handoff=60s; stale_ping=10m_without_meaningful_progress; stale_reclaim=20m_to_30m_policy_dependent
allowed prefixes: git status; git diff; git add/git commit/git push when commit or push policy delegates it; project test/build commands detected by preflight
restricted prefixes: rm -rf; git reset --hard; git checkout --; production deploy; destructive database commands; credential prompts
verification: focused_plus_build; full gate=risk_triggered; browser=screenshots
review routing: risk_triggered; spawn=after_handoff
cleanup: none; keep recent=3
stop/resume: policy=enabled; default=drain_to_checkpoint; scope=all_factory; authority=principal_or_user; monitors=pause_after_stop; cleanup=rolling_window_after_checkpoint; resume=resume_from_stop_packet; default_resume=continue_same_baton; packet_required=true
blockers: git_auth=local_commit_continue; dirty=pause_reconcile; push=local_only
```

## Baton Queue

| Baton | Tier | Owner | Status | Objective | Verification | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| B-001 | integration | executive thread (single writer) | accepted | Port data tables + protobuf encoder from index.html to Python `d4filter/` package; establish golden byte-comparison tests | pytest incl. node-run golden harness | repeat-data typo risk; golden harness fidelity |
| B-002 | integration | executive thread (single writer) | accepted | Maxroll guide fetch + parser + one-shot CLI skeleton | focused parser fixture tests | site selector brittleness |
| B-003 | integration | executive thread (single writer) | accepted | Mapper with aliases + interactive resolution | focused mapper tests + manual smoke | ambiguity silently dropping stats |
| B-004 | integration | executive thread (single writer) | accepted | Mobalytics parser, richer rule tiers, class detection/gating | focused tests + real-guide smoke | rule-order reversal bug |
| B-005 | integration | executive thread (single writer) | accepted | Chrome extension (MV3): content scripts read guide payloads on open maxroll/mobalytics tabs; popup generates import codes with the richer tier stack; JS data/encoder generated from index.html to avoid drift | node-driven parity tests vs Python + fixture smoke | MV3 CSP constraints; site payload drift; profile-build hydration timing |
| B-006 | integration | executive thread (single writer) | accepted | Per-profile variants: expose maxroll planner profiles as `variants`, add CLI `--variant` and popup Variant selector, map prose stat paragraphs, fix abbreviation matching | pytest incl. rogue fixture parity (merged + Bossing) and node popup harness | variant name drift across guides; prose over-match |
| B-007 | integration | executive thread (single writer) | accepted | Curate mobalytics prose: parse per-paragraph Lexical blocks, drop skill-description prose, and only count paragraphs with recommendation cues | focused mapper/parser tests + extension byte parity | cues could miss legitimate advice |

## Acceptance Evidence

| Baton | Tier | Evidence | Skipped checks | Residual risk |
| --- | --- | --- | --- | --- |
| B-001 | integration | 2026-10-09: `pytest` 12/12 pass. 6 golden cases byte-identical (base64 string equality) between `d4filter.filter_mirror.build_mirror_filter` and the live JS encoder from index.html executed under node via `tools/golden_harness.js`; includes empty filter, skill-only, full hf-warlock preset, duplicate stats, and no-gold-branch paths. Unit tests cover varint continuation bits, field headers, condition shapes. | manual in-game import not performed this slice | Python data tables are a copy of index.html; drift between the two is possible until synced automatically (tracked as open decision) |
| B-002 | integration | 2026-10-09: `pytest` 23/23 pass. Parser tests against a saved 550KB fixture of the live Hell Fracture Warlock guide; extracts title/class/season/profiles, named skills, skill-bar IDs, Important Stats lines, and the guide's own 3 authored filter codes. Live smoke test: `d4filter.cli https://maxroll.gg/d4/build-guides/hell-fracture-warlock-guide` fetches and parses correctly with plausible UA | mapper does not exist yet; Mobalytics untouched; Important Stats prose varies across guides | maxroll page redesign or Remix context schema change will break the parser; fixture guards current shape |
| B-003 | integration | 2026-10-09: `pytest` 37/37 pass (full gate at the B-003 boundary incl. re-run golden parity). Mapper resolves real guide prose end to end: fixture guide generates a valid import code with core [Attack Speed, Critical Strike Chance], secondary [Maximum Life, Lucky Hit Restore Primary Resource], confirmed skills [Hell Fracture, Sigil of Chaos, Sigil of Subversion]. Interactive resolver prompts with fuzzy suggestions and persists user aliases to `~/.config/d4filter/aliases.json`, covered by tests with monkeypatched stdin. | live in-game import still not performed; Abyss-Skills rank line unmatched by design (temper phrasing) | fuzzy threshold 0.72 could over-match short strings; aliases persist per-user only |
| B-004 | integration | 2026-10-09: `pytest` 45/45 pass. Mobalytics fixture (920KB, saved with browser-like headers after plain UA got 403) parses class/season/title from doc tags, collapses skill variant labels to base skills, extracts rich-text prose for stat mapping via `mapper.map_prose`. Richer tiers verified: violet near-BiS rule embedded, `--mirror` mode remains byte-compatible with web tool. Class-aware dead-resource hiding derives from CLASS_RESOURCES map (Warlock hides Fury regen, Barbarian keeps it). Live fetch of the mobalytics guide succeeds with the browser-like header set; `d4filter` console script installed via pip -e. | heavy prose matching over-maches casual word usage (Strength/Armor/Damage Reduction/Lucky Hit Chance appear from descriptive text, not affix lists) — needs curated suppression or per-slot affix tables; Metamorphosis/Hellfire for non-Warlock classes remain unconfirmed | prose false positives inflate secondary tier; seasonal guide redesign; mobalytics 403 for plain-UA agents (handled via full browser headers) |
| B-005 | integration | 2026-10-09: `pytest` 54/54 pass. Extension JS pipeline (generated core + ported parsers/mapper/tiers) produces base64 **byte-identical** to the Python CLI for both saved fixtures end to end. `tools/sync_extension_data.py` regenerates `extension/lib/core.js` from index.html with a staleness-guard test. Popup classic-script load order verified in a node vm simulation (caught and fixed a top-level `const` collision between lib files — wrapped in IIFEs). Guide-spec JS parsers return the same class/season/skills/stat counts as Python. | No real-browser load test (no Chrome automation available in this environment); profile-build URLs (e.g. SOJ PEN variant) have empty preloaded state — client-rendered only, so the extension content-script route is the planned fix but is untested against a live profile tab; interactive alias editing not in popup v1 (unmatched stats listed read-only) | Site payload drift affects extension identically to CLI; MV3 store review may flag broad host matches (maxroll/mobalytics only, acceptable) |
| B-006 | integration | 2026-10-10: `pytest` 62/62 pass. Maxroll planner profiles parse into `GuideSpec.variants` with per-profile stat lines and skills; `--variant`/popup selector narrow extraction while the default merges all profiles. New Rogue fixture (Dance of Knives) guards sentence-style stat advice: prose paragraphs now yield Damage Over Time, Poison, and Vulnerable multipliers. Extension JS and Python agree byte-for-byte for the rogue guide both merged and narrowed to Bossing. Found and fixed a latent Python-only bug: abbreviation targets were lowercase while `DB` keys are title case, so the abbreviation branch never fired in Python (JS used a lowercase index and did fire); both now use word-boundary regexes and canonical DB names, which also stops "cc" matching inside words like "according". | No live-guide fetch or in-game import this slice; popup Variant selector exercised only through the node harness | Variant names are site-defined and may drift; prose scan can pick up affixes mentioned incidentally in explanatory text |
| B-007 | integration | 2026-10-10: `pytest` 67/67 pass. Mobalytics prose now parses as per-paragraph/list-item Lexical blocks from `simplifiedContent` only (skill tooltips in `descriptionAssignedSkills` are excluded), and a paragraph must contain a recommendation cue (stack, temper, look for, prioritise, affix, roll, in other slots) before its DB names count. Fixture result went from a noisy secondary tier (Strength, Willpower, Armor, Damage Reduction, Lucky Hit Chance) to Maximum Life, Fire Resistance, Lucky Hit Restore Primary Resource, while gaining Resource Cost Reduction and keeping the guide's real core goals. JS guide-spec/mapper mirror the change and the extension still emits byte-identical codes for both sites; the node popup harness now also covers the mobalytics and rogue-variant paths. | No live mobalytics fetch; cue list tuned against one fixture | A guide that gives advice without cue words will under-map; new guides may need new cues |

## Open Decisions

| ID | Decision | Owner | Status | Notes |
| --- | --- | --- | --- | --- |
| D-001 | Single source of truth for DB/SKILLS | executive | open | index.html holds originals; d4filter/data.py is a copy. Keep both in sync manually until (or unless) index.html is generated from data.py. Automated parity test is an option. |
| D-002 | Maxroll guide content parsing channel | executive | decided | Parse `window.__remixContext` JSON (plannerProfile + widgetNotes + data.lootFilters) rather than scraping visible HTML. HTML shell is a Remix client shell with no article content in markup. Verified against live Season 15 guide and saved fixture. |
| D-003 | Mobalytics guide content parsing channel | executive | decided | Plain fetches get 403; full browser-like header set (Chrome UA + Sec-Fetch-*) succeeds (920KB HTML). Parse `window.__PRELOADED_STATE__` → `diablo4State.apollo.graphqlV2.queries[].state.data[].game.documents.userGeneratedDocumentBySlug.data`: tags give class/season, `static-data-widget` nodes with `groupId="skills"` give skills (split variant labels on `:`), `simplifiedContent` Lexical trees give stat prose. doc-level `data.lootFilter` is null in this fixture. |

## Retrospective

| Date | Observation | Adjustment |
| --- | --- | --- |
| 2026-10-10 | Python and JS abbreviation matching had silently diverged: JS indexed DB by lowercase and matched, Python compared lowercase targets against title-case keys and never matched, so fuzzy matching was masking the gap. | Keep abbreviation targets canonical and word-bounded in both ports; extend parity fixtures whenever a new site shape appears. |

## Next Baton Candidate

Hardening backlog (candidate batons B-008+):

- In-game import verification of at least one maxroll-derived and one mobalytics-derived code (manual, user-assisted).
- DB parity test between index.html and d4filter/data.py (decides D-001).
- Interactive confirmation of skill-rank line handling ("Ranks to X" lines).
- CLI polish: error paths for non-guide URLs, cache TTL flag, structured output (--json).
- Confirm non-Warlock skill IDs so Rogue/Barbarian/etc. variant skills reach the filter instead of being dropped as unconfirmed.
- Re-check the prose cue list against two or three more live guides from each site.

```text
Define B-008 with objective, write scope, non-goals, risk, acceptance tier, and verification.
```

## Persistent Goal

```text
Drive the d4-filter-generator software factory in Velocity Mode: deliver product-visible vertical slices quickly, coordinate batons, preserve hard invariants, use focused verification per slice, run full gates at configured checkpoints, record known risks, commit accepted integration work, and continue until this outcome is ready for hardening or release: d4filter CLI: scrape maxroll/mobalytics build guides and emit D4 loot filter import codes
```
