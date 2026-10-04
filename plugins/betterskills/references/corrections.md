# Mining Corrections from Session History

Corrections are the raw material of every skill (R1) and every revision
(R4). Claude Code stores each session as JSONL under
`~/.claude/projects/<project-slug>/<session-id>.jsonl`. The jq program
`corrections.jq` (next to this file) lists user messages that read as
corrections, each with the tail of the assistant message it answered.

## Run it

Last 30 days, all projects:

```bash
find ~/.claude/projects -name '*.jsonl' -mtime -30 -print0 \
  | xargs -0 jq -nrR -f "${CLAUDE_PLUGIN_ROOT}/references/corrections.jq"
```

Narrow it:

- **Window** — change `-mtime -30` (`-mtime -7` for the weekly loop).
- **Project** — add `-path '*<project-name>*'` to `find`.
- **Behavior** — pipe through `grep -i -A1 '<topic>'` to keep only
  corrections about what one skill targets.

Output, two lines per hit:

```
2026-10-03  -Users-me-myrepo  No, too long. Just bullets.
    after: …Here are three pages of release notes with an intro.
```

The filter matches phrasing ("no", "instead", "I said", "again", "that's
not", "you forgot", "too long", "why did you", …) and over-reports. A hit
is a correction only when the user rejected or changed Claude's output.

## Turn hits into candidates

1. Drop hits that are not corrections (a "no" answering a question, a fix
   to the user's own typo).
2. Cluster the rest by the behavior corrected, not by wording. "Too
   long", "shorter please" and "just the answer" are one cluster.
3. Count each cluster and the distinct sessions it spans. A correction
   made once is noise; one made across sessions is a skill candidate.
4. For each cluster, name the **failing step** (R1.b) and write the fix
   as one sentence of desired behavior (R4.b).
5. Check whether an installed skill or a `CLAUDE.md` rule already covers
   the cluster (R5.c). If one does, the finding is a revision to it, not
   a new skill.

## When there is no history

Ask the user: "What output did you last send back, and what did you
change?" One question at a time, until you have the correction and the
failing step.
