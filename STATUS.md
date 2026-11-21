# STATUS

Read `RULES.md` first. Update this file at the end of every run.

_Last updated: 2026-11-21 (setup run)_

## Done

- Tools installed in the cloud container: ffmpeg 6.1.1, yt-dlp 2026.10.26,
  PySceneDetect 0.7.3 (OpenCV backend), faster-whisper 1.2.1.
- `RULES.md` written: approval-only posting, gauntlet rule, no keys in chat, keep STATUS current.
- `CLAUDE.md` added so every session reads `RULES.md` and `STATUS.md` first.

## Waiting on the owner

- [ ] Connect Composio to claude.ai (see "Composio setup" below), then start a new session.
- [ ] In Composio, connect: YouTube, Instagram, Apify.
- [ ] Connect TikTok through Upload-Post (see "Composio setup" below).
- [ ] Decide the footage source policy (see "Open questions").

## Blocked

- Any platform action (reading channel stats, scraping, uploading) is blocked until the
  Composio connector is live in a session.

## Awaiting approval

_(none)_

## Gauntlet log

_(none)_

## Composio setup

Not done yet. Steps given to the owner on 2026-11-21:
1. composio.dev → sign in → create an MCP server / config that includes the YouTube,
   Instagram, and Apify toolkits; authorize each account through Composio's OAuth screens.
2. Copy the MCP server URL Composio gives you.
3. claude.ai/customize/connectors → add a custom connector → paste that URL.
4. Upload-Post (upload-post.com): sign up and link the TikTok account there. If Composio
   lists an Upload-Post toolkit, add it to the same MCP server; if not, its API key goes
   in through the environment's secure credential form, never in chat.
5. Start a new Claude Code session on this repo (connectors load when a session starts).

## Open questions

- Footage source: own gameplay captures vs. clips of other creators or Rockstar trailers.
  The second carries Content ID / copyright-strike risk on all three platforms.

## Next run

1. Confirm the Composio tools are present; list connected accounts.
2. Record the channel handles here.
3. No posting until the owner approves specific items (RULES.md rule 1).
