# d4-filter-generator Build Ledger

Initialized: 2026-10-09

## Current Factory State

```text
status: running / baton in progress
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
current_baton: B-001
last_accepted_baton: none
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
| B-002 | integration | queued | pending | Maxroll guide fetch + parser + one-shot CLI skeleton | focused parser fixture tests | site selector brittleness |
| B-003 | integration | queued | pending | Mapper with aliases + interactive resolution | focused mapper tests + manual smoke | ambiguity silently dropping stats |
| B-004 | integration | queued | pending | Mobalytics parser, richer rule tiers, class detection/gating | focused tests + real-guide smoke | rule-order reversal bug |

## Acceptance Evidence

| Baton | Tier | Evidence | Skipped checks | Residual risk |
| --- | --- | --- | --- | --- |
| B-001 | integration | 2026-10-09: `pytest` 12/12 pass. 6 golden cases byte-identical (base64 string equality) between `d4filter.filter_mirror.build_mirror_filter` and the live JS encoder from index.html executed under node via `tools/golden_harness.js`; includes empty filter, skill-only, full hf-warlock preset, duplicate stats, and no-gold-branch paths. Unit tests cover varint continuation bits, field headers, condition shapes. | manual in-game import not performed this slice | Python data tables are a copy of index.html; drift between the two is possible until synced automatically (tracked as open decision) |

## Open Decisions

| ID | Decision | Owner | Status | Notes |
| --- | --- | --- | --- | --- |
| D-001 | Single source of truth for DB/SKILLS | executive | open | index.html holds originals; d4filter/data.py is a copy. Keep both in sync manually until (or unless) index.html is generated from data.py. Automated parity test is an option. |

## Retrospective

| Date | Observation | Adjustment |
| --- | --- | --- |

## Next Baton Candidate

```text
Define B-001 with objective, write scope, non-goals, risk, acceptance tier, and verification.
```

## Persistent Goal

```text
Drive the d4-filter-generator software factory in Velocity Mode: deliver product-visible vertical slices quickly, coordinate batons, preserve hard invariants, use focused verification per slice, run full gates at configured checkpoints, record known risks, commit accepted integration work, and continue until this outcome is ready for hardening or release: d4filter CLI: scrape maxroll/mobalytics build guides and emit D4 loot filter import codes
```
