# STATUS

Read `RULES.md` first. Update this file at the end of every run.

_Last updated: 2026-11-21 (step 2 run)_

## Pipeline progress (the 9-step plan)

| Step | State |
|---|---|
| 1 Setup | Done, except platform connections (replaced: see "Free substitutes") |
| 2 Find videos that blow up | **Paused: waiting for the owner to OK the channel list** |
| 3 Thumbnail/title study | Not started (needs step 2) |
| 4 Grab best clips | Not started; needs Twitch/Kick/TikTok network hosts |
| 5 Edit episode | Not started |
| 6 Vertical clips | Not started |
| 7 Own video script | Not started; needs owner's gameplay |
| 8 Gauntlet check | Rule in place (RULES.md rule 2) |
| 9 Post | Manual by owner after approval |

## Free substitutes (owner asked: no paid tools)

| Paid tool in the plan | Free substitute | Status |
|---|---|---|
| Apify YouTube channel scraper | `yt-dlp` search + channel RSS feeds (`scripts/find_channels.py`, `scripts/find_outliers.py`) | Working |
| Apify Twitch/Kick/TikTok clip scraper | `yt-dlp` + public endpoints | Untested; hosts blocked until allowed |
| Composio (YouTube/Instagram posting) | Owner uploads manually from `out/` after approval | Planned |
| Upload-Post (TikTok) | Owner uploads manually | Planned |
| gpt-image / nano banana pro thumbnails | Pillow + ffmpeg composites from real gameplay frames | Planned |
| Clipping campaign submission | Owner submits manually | Planned |

Network allowed so far: www.youtube.com, youtube.com, i.ytimg.com.

## Done

- Tools installed: ffmpeg 6.1.1, yt-dlp 2026.10.26, PySceneDetect 0.7.3, faster-whisper 1.2.1.
  The environment setup script reinstalls them in new sessions (unproven until a fresh session).
- `RULES.md`, `CLAUDE.md` written.
- Step 2a: `data/channels.csv`: 161 active English GTA channels (uploaded in last 14 days,
  >=30% GTA titles in last 15 uploads), ranked by median views of last 15 uploads.

## Waiting on the owner

- [ ] OK the channel list (or edit it). Approved channels go in `data/channels_approved.csv`
      (columns: channel,url). Then step 2b runs: `python3 scripts/find_outliers.py`.
- [ ] Decide footage source policy (see "Open questions").

## Awaiting approval

_(none)_

## Gauntlet log

_(none)_

## Open questions

- Footage source: other creators' / streamers' clips carry Content ID and copyright-strike
  risk even with credit; credit is not permission. Clipping campaigns (where the streamer
  pays for clips) are the lower-risk route for step 6.
- Weekly re-run of step 2 (prompt 2): set up as a scheduled task once the list is approved.

## Next run

1. If `data/channels_approved.csv` exists, run step 2b and report outliers + what changed.
2. Then step 3.
