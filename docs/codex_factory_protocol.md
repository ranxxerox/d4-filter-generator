# d4-filter-generator Codex Factory Protocol

## Configuration

- Work mode: `velocity`
- Target outcome: `d4filter CLI: scrape maxroll/mobalytics build guides and emit D4 loot filter import codes`
- Goal policy: `none`
- Role topology: `lean_solo`
- User involvement: `hands_off`
- Feedback handling: `no_manager`
- Principal policy: `none`
- Principal authority: `observe`
- Principal intervention: `no_baton_interference`
- Config verbosity: `compact`
- Topology: `executive_as_ledger`
- Acceptance tier: `integration`
- Reviewer policy: `risk_triggered`
- Reviewer spawn: `after_handoff`
- Manager policy: `none`
- Verification: `focused_plus_build`
- Full gate cadence: `risk_triggered`
- Permission profile: `full_access`
- Approval policy: `on_failure`
- Tool-call budget policy: `bounded_reads`
- Thread-read policy: `latest_only`
- Active actor polling: `adaptive_backoff`
- Model switch policy: `by_role`
- Capability preflight: `minimal`

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

## Roles

- Principal Executive: user-facing strategic partner; oversees topology, mode, cleanup, handoffs, ledger promotion, and emergency intervention according to configured authority.
- Executive: product judgment, routing, final acceptance, commit policy, and user communication.
- Ledger/controller: build ledger, baton assignment, evidence, risks, and recovery notes.
- Builder: scoped implementation and Handoff Bundle to Executive/Ledger without committing unless delegated.
- Reviewer: read-only Review Package to Executive/Ledger by default.
- Manager/User Liaison: user feedback intake and Principal/Executive Briefs only; no direct Builder/Reviewer control by default.
- Watcher: monitor only; never edits files.

## Operating Rules

- Preserve one active writer per worktree unless explicitly configured otherwise.
- Principal may steer or reconfigure the factory only through the configured intervention policy and should not interrupt an active writer except for safety, user override, or factory-health recovery.
- Prefer handoff sequencing; use parallel read-only reviewers for speed.
- Record assignment before authorization when git is available.
- Route Builder handoffs through Executive/Ledger before any Reviewer work.
- Take review lock only after handoff, block, stall, relinquish, or reclaim.
- If push/auth fails, keep local commits and continue with recorded remote status.
- If runtime permissions are weaker than configured, record the mismatch and apply blocker fallbacks instead of silently downgrading quality.
- Use the configured model/reasoning by role when thread tools support it; otherwise restate the target model policy in worker prompts.
- Keep ledgers useful, not ceremonial.
- Stop directives freeze new assignments immediately, then follow the configured stop mode and produce a Stop Packet when required.
- Escalate to stricter verification when risk escalators are touched.
- Run thread cleanup only after ledger evidence captures completed work.

## Stop And Resume

Default stop mode: `drain_to_checkpoint`

- `pause_new_work`: stop assigning new batons; current safe work may continue.
- `drain_to_handoff`: active Builder reaches a Handoff Bundle, then pauses before acceptance.
- `drain_to_checkpoint`: active baton reaches review, acceptance, ledger evidence, and configured commit/push fallback, then pauses.
- `release_freeze`: stop feature work; allow only release gates, blocker fixes, and readiness notes.
- `hard_stop`: active actors stop after the current safe command and record dirty state.
- `emergency_stop`: immediate freeze for safety, security, destructive-action, or ownership risk.

Stop authority is `principal_or_user`. Stop scope is `all_factory`. Monitor handling is `pause_after_stop`. Resume uses `resume_from_stop_packet` with default mode `continue_same_baton`.

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

## Verification

- Configured full gate: `Record the project full test/eval command here.`
- Configured generated-file guards: Record generated files that must not be staged.
- UI/browser QA policy: `screenshots`
- Thread cleanup policy: `none`
