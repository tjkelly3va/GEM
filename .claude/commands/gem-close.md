---
description: Close the GEM session — run the SKILL.md close checklist, then commit.
---

Close the current GEM session.

**`SKILL.md` §Session Close is the authority for every step below.** This command
is the invocation and the commit; it deliberately does not restate the checklist,
because two copies of a procedure is the drift class this project exists to fight.
Read §Session Close and follow it as written.

Order is load-bearing. Do not reorder:

1. Confirm every in-session edit is written to the canonical directory.
2. If any policy's HCPCS code references or any `gem:CodeGroup` membership changed,
   re-run the `gem:refersToCodeGroup` linking pass. `codegroup_link_drift` and
   `codegroup_block_extent` must both be GREEN before proceeding.
3. **Write the new handoff first**, so its `Session N` title is on disk before the
   audit runs. This is what makes the `empirical_counts` marker target N instead of
   N−1 (the Fix-A protocol, S237).
4. Run the audit with `--autofix`. Confirm GREEN, and confirm the empirical-counts
   marker in `SKILL.md` reads **S{N}**, not S{N−1}. Any later rewrite of `SKILL.md`
   reopens the lag and requires re-running this step.
5. **Compute the §1 table LAST.** Hash and size all 15 canonical files only after
   every one is in its final state, then write the table into the new handoff. Any
   canonical file touched after the table is computed silently invalidates its row
   and yields a spurious `hash_verify` RED at the next bootstrap.
6. Commit:

       git add -A
       git commit -m "S{N}: <one-line summary>"

   The handoff and the source PDFs are part of the commit. **Never push.**

7. Report: what changed, the audit tier counts, the INFO queue totals, the NCD
   census line, and the commit SHA.

If the audit is not GREEN at step 4, stop and surface the finding. Do not compute
the §1 table over an unclean set, and do not commit.
