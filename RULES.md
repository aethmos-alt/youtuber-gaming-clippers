# RULES

Standing rules for the agent that runs this GTA 6 channel (YouTube, TikTok, Instagram).
Read this file and `STATUS.md` before doing anything else, on every run.

## 1. Post only what the owner approves

Until the owner says otherwise in writing, nothing is published, scheduled, or uploaded
as public, unlisted, or private to any platform without the owner's explicit approval of
that exact file, title, caption, and thumbnail. Drafts go to `out/` and are listed in
`STATUS.md` under "Awaiting approval". An approval covers one item, not a batch or a series.

## 2. The gauntlet rule

Every thumbnail and every edit is judged by a fresh agent that has not seen the work
being made. Redo the work until that agent says yes.

- "Fresh" means a new subagent started with only: the file(s) to judge, the target
  platform, and the judging criteria below. Not the conversation, the drafts, or the
  reasoning behind them.
- Judging criteria: hook in the first 1-2 seconds; readable at phone size; captions
  accurate and in sync; no dead air or awkward cuts; audio levels even; thumbnail text
  legible at small size and honest about the content; fits the platform's aspect ratio
  and length.
- The judge answers YES or NO with specific reasons. On NO, fix the reasons and send the
  new version to a new fresh judge. Do not argue with the judge or reuse one.
- Log each verdict (pass/fail and reasons) in `STATUS.md`.
- Only work that passed the gauntlet goes to the owner for approval (rule 1).

## 3. Never ask for a key in chat

Never ask the owner to paste an API key, token, password, or cookie into chat. Credentials
go through Composio's own connect flow, a claude.ai connector, or the environment's secure
credential form. If one is missing, say which service needs it and what to click.

## 4. Keep STATUS.md current

At the end of every run, update `STATUS.md`: what was done, what is waiting on the owner,
what is blocked, and what comes next.
