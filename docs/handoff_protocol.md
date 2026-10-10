# d4-filter-generator Handoff Protocol

Configured detail level: `compact`

```text
# Handoff: B-XXX / <slice>

## State
- Branch/worktree:
- Base commit:
- Worktree status:
- Baton owner:
- Acceptance tier targeted:

## Work Completed
- Files changed:
- Behavior implemented:
- Contracts/data/API changed:
- Decisions made:

## Verification
- Commands run:
- Passing:
- Failing:
- Skipped and why:
- Browser/visual QA:

## Risk and Acceptance
- Risk escalators touched:
- Acceptance tier support:
- Hard invariants preserved:
- Residual risk:

## Next Recommendation
- Accept / patch / reassign:
- Next baton:
- Do not touch:
```

## Factory Stop Directive

Configured default: `drain_to_checkpoint`

```text
Factory stop directive for d4-filter-generator.

Mode:
<pause_new_work|drain_to_handoff|drain_to_checkpoint|release_freeze|hard_stop|emergency_stop>

Scope:
<new_work_only|active_baton|all_factory|monitors_only|cleanup_only>

Authority:
<requester and configured authority>

Reason:
<why stopping now>

Instructions:
- Stop assigning new batons immediately.
- If you own active work, finish only the current safe command if interrupting it would corrupt state.
- Do not stage, commit, push, archive threads, or change monitors unless this directive explicitly authorizes it.
- Report current baton, worktree status, dirty files, running/last commands, verification state, risks, and exact resume point.
```

## Stop Packet

```text
mode:
scope:
reason:
requested_by:
authority:
stop_state:
executive_or_ledger:
principal:
manager:
active_builder:
active_reviewer:
current_baton:
branch_or_worktree:
latest_accepted_commit:
push_or_remote_status:
dirty_files:
staged_files:
untracked_files:
running_or_last_command:
completed_checks:
unfinished_checks:
monitors_kept:
monitors_paused_deleted_or_retargeted:
threads_archived:
threads_preserved:
unresolved_risks:
resume_policy:
resume_authority:
next_recommended_action:
verification_to_rerun:
cleanup_still_pending:
```

## Resume Packet

```text
requested_by:
approved_by:
resume_policy:
resume_mode:
prior_stop_packet:
executive_or_ledger_to_wake:
principal_or_manager_to_notify:
builder_or_reviewer_to_resume_or_replace:
monitors_to_restart:
cleanup_to_defer_or_run:
next_baton:
write_owner:
review_owner:
worktree_or_branch:
verification:
risks_to_recheck:
```
