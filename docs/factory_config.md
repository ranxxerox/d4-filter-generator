# d4-filter-generator Factory Configuration

Initialized: 2026-10-09
Last updated: 2026-10-09

## Operating Model

```text
work_mode: velocity
factory_topology: executive_as_ledger
role_topology: lean_solo
user_involvement: hands_off
feedback_handling: no_manager
principal_policy: none
principal_authority: observe
principal_intervention_policy: no_baton_interference
principal_digest_cadence: checkpoint
principal_context_budget: compact
config_verbosity: compact
target_outcome: d4filter CLI: scrape maxroll/mobalytics build guides and emit D4 loot filter import codes
goal_policy: none
goal_text: Drive the d4-filter-generator software factory in Velocity Mode: deliver product-visible vertical slices quickly, coordinate batons, preserve hard invariants, use focused verification per slice, run full gates at configured checkpoints, record known risks, commit accepted integration work, and continue until this outcome is ready for hardening or release: d4filter CLI: scrape maxroll/mobalytics build guides and emit D4 loot filter import codes
acceptance_tier: integration
baton_size: vertical_slice
concurrency_policy: single_writer
reviewer_policy: risk_triggered
reviewer_spawn_policy: after_handoff
manager_policy: none
executive_context_policy: direct_user_chat
verification_level: focused_plus_build
full_gate_cadence: risk_triggered
browser_qa_policy: screenshots
review_depth: targeted
handoff_detail: compact
package_protocol: compact
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
external_effect_policy: explicit_operator
model_policy: Use the user's preferred capable model and reasoning level unless a baton explicitly lowers risk and cost.
role_model_policy: principal=user-preferred capable model/high; executive=user-preferred capable model/high; ledger=user-preferred capable model/high; builder=user-preferred capable model/high; reviewer=user-preferred capable model/high; manager=user-preferred capable model/high; watcher=user-preferred capable model/high; fallback=user-preferred capable model/high
model_switch_policy: by_role
default_model: user-preferred capable model
default_reasoning: high
principal_model: user-preferred capable model
principal_reasoning: high
executive_model: user-preferred capable model
executive_reasoning: high
ledger_model: user-preferred capable model
ledger_reasoning: high
builder_model: user-preferred capable model
builder_reasoning: high
reviewer_model: user-preferred capable model
reviewer_reasoning: high
manager_model: user-preferred capable model
manager_reasoning: high
watcher_model: user-preferred capable model
watcher_reasoning: high
fallback_model: user-preferred capable model
fallback_reasoning: high
design_skill_policy: Use the project-specified design skill for UI work.
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
allowed_command_prefixes: git status; git diff; git add/git commit/git push when commit or push policy delegates it; project test/build commands detected by preflight
restricted_command_prefixes: rm -rf; git reset --hard; git checkout --; production deploy; destructive database commands; credential prompts
destructive_action_policy: confirm
external_network_policy: allowed
credential_policy: use_existing_only
capability_preflight: minimal
git_auth_policy: local_commit_continue
dirty_worktree_policy: pause_reconcile
generated_file_policy: guard_and_skip
test_flake_policy: rerun_once
long_test_policy: focused_then_checkpoint
dev_server_policy: reuse_or_start
worktree_policy: explicit_only
branch_policy: current_branch
commit_policy: per_vertical_slice
push_policy: local_only
browser_tool_policy: in_app_first
context_compaction_policy: handoff_summaries
heartbeat_policy: handoff_triggered
artifact_policy: record_paths
user_interrupt_policy: executive_direct
release_readiness_policy: risk_triggered
full_gate_command: Record the project full test/eval command here.
generated_file_guards: Record generated files that must not be staged.
```

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

## Capability Preflight

Configured level: `minimal`

| Capability | Status | Evidence | Blocker policy |
| --- | --- | --- | --- |
| thread tools | unknown | inspect at launch | context/heartbeat policy |
| thread tool schema | unknown | inspect at launch | tool_call=bounded_reads |
| thread read policy support | unknown | inspect at launch | thread_read=latest_only |
| tool call limits | unknown | inspect at launch | polling=adaptive_backoff |
| automation tools | unknown | inspect at launch | heartbeat=handoff_triggered |
| goal tooling | unknown | inspect at launch | goal_policy=none |
| git write | unknown | inspect at launch | commit=per_vertical_slice |
| push auth | unknown | inspect at launch | git_auth=local_commit_continue; push=local_only |
| network | unknown | inspect at launch | external_network=allowed |
| browser | unknown | inspect at launch | browser_tool=in_app_first |
| package manager | unknown | inspect at launch | long_tests=focused_then_checkpoint |
| test commands | unknown | inspect at launch | flakes=rerun_once |
| env files | unknown | inspect at launch | credentials=use_existing_only |
| required secrets | unknown | inspect at launch | credentials=use_existing_only |
| generated files | unknown | inspect at launch | generated_files=guard_and_skip |
| dev server | unknown | inspect at launch | dev_server=reuse_or_start |

## Principal And Feedback Policy

- User involvement: `hands_off`
- Feedback handling: `no_manager`
- Principal policy: `none`
- Principal authority: `observe`
- Principal intervention policy: `no_baton_interference`
- Principal digest cadence: `checkpoint`
- Principal context budget: `compact`
- Manager policy: `none`
- Executive context policy: `direct_user_chat`

Principal Executive oversees mode, topology, cleanup, handoffs, ledger promotion, and factory health according to its authority. It does not normally hold the write baton.

## Stop And Resume Policy

- Factory stop policy: `enabled`
- Default stop mode: `drain_to_checkpoint`
- Stop scope: `all_factory`
- Stop authority: `principal_or_user`
- Stop monitor policy: `pause_after_stop`
- Stop cleanup policy: `rolling_window_after_checkpoint`
- Resume policy: `resume_from_stop_packet`
- Default resume mode: `continue_same_baton`
- Stop packet required: `true`

Stop requests preempt new baton assignment. Unless the mode is `emergency_stop`, capture the active baton, owner, worktree status, latest commit/push state, monitors, cleanup actions, risks, and resume instructions before pausing or archiving factory actors.

## Permission And Model Policy

- Permission profile: `full_access`
- Sandbox mode requested: `full_access`
- Approval policy requested: `on_failure`
- Destructive action policy: `confirm`
- External network policy: `allowed`
- Credential policy: `use_existing_only`
- Tool-call budget policy: `bounded_reads`
- Thread-read policy: `latest_only`
- Active actor polling policy: `adaptive_backoff`
- Active Builder poll interval: `3m`
- Long-check poll interval: `5m`
- Handoff poll interval: `60s`
- Stale ping after: `10m_without_meaningful_progress`
- Stale reclaim after: `20m_to_30m_policy_dependent`
- Model policy: Use the user's preferred capable model and reasoning level unless a baton explicitly lowers risk and cost.
- Role model policy: principal=user-preferred capable model/high; executive=user-preferred capable model/high; ledger=user-preferred capable model/high; builder=user-preferred capable model/high; reviewer=user-preferred capable model/high; manager=user-preferred capable model/high; watcher=user-preferred capable model/high; fallback=user-preferred capable model/high
- Model switch policy: `by_role`

If the runtime cannot apply these settings directly, record the mismatch in the ledger and use the blocker policy fallback.

## Blocker Policies

```text
git_auth_policy: local_commit_continue
dirty_worktree_policy: pause_reconcile
generated_file_policy: guard_and_skip
test_flake_policy: rerun_once
long_test_policy: focused_then_checkpoint
dev_server_policy: reuse_or_start
worktree_policy: explicit_only
branch_policy: current_branch
commit_policy: per_vertical_slice
push_policy: local_only
browser_tool_policy: in_app_first
context_compaction_policy: handoff_summaries
heartbeat_policy: handoff_triggered
artifact_policy: record_paths
user_interrupt_policy: executive_direct
release_readiness_policy: risk_triggered
```

## Acceptance Ladder

- Prototype accepted: demonstrable behavior with explicit hardening gaps.
- Integration accepted: wired behavior with focused evidence and no known blocking regressions.
- Release accepted: full release evidence, deployment readiness, and final QA.

## Risk Escalators

Escalate verification and review when touching auth/security, secrets, payments, production data writes, database migrations, public contracts, infra/deployment, background jobs, external live services, ML/eval/scoring logic, or generated clients.

## Persistent Goal

Goal policy: `none`

```text
Drive the d4-filter-generator software factory in Velocity Mode: deliver product-visible vertical slices quickly, coordinate batons, preserve hard invariants, use focused verification per slice, run full gates at configured checkpoints, record known risks, commit accepted integration work, and continue until this outcome is ready for hardening or release: d4filter CLI: scrape maxroll/mobalytics build guides and emit D4 loot filter import codes
```

## Project-Specific Invariants

- Generated-file guards: Record generated files that must not be staged.
- External effects: explicit_operator
- Full gate: `Record the project full test/eval command here.`
