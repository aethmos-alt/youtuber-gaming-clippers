# STATUS

Read `RULES.md` first. Update this file at the end of every run.

_Last updated: 2026-11-21 (steps 2-8 run)_

## Pipeline progress (the 9-step plan)

| Step | State | Output |
|---|---|---|
| 1 Setup | Done (paid connectors replaced, see below) | `RULES.md`, `CLAUDE.md`, env setup script |
| 2 Find outliers | **Done.** Owner approved 35 channels | `data/channels_approved.csv`, `data/outliers.csv` (119 GTA outliers) |
| 2 weekly rerun | Waiting: owner's time zone for the schedule | `scripts/find_outliers.py` prints what changed |
| 3 Thumbnails/titles | Study done; tool built; script titles passed gauntlet | `THUMBNAILS.md`, `scripts/make_thumbnail.py` |
| 4 Grab clips | **Blocked: needs owner's free Twitch developer app** (see below) | none |
| 5 Edit episode | Tool built and tested on synthetic clips | `scripts/make_episode.py` |
| 6 Verticals | Tool built and tested on synthetic clip | `scripts/make_vertical.py` |
| 7 Own video | **Script written: waiting on owner to record** | `script.md` |
| 8 Gauntlet | Packager + judge brief built; tested twice | `scripts/gauntlet_pack.py`, `gauntlet/JUDGE.md` |
| 9 Post | Manual by owner after approval (Composio replaced) | none yet |

## Free substitutes (owner asked: no paid tools)

| Paid tool in the plan | Free substitute | Status |
|---|---|---|
| Apify YouTube scraper | yt-dlp search + channel RSS + flat channel listings | Working |
| Apify Twitch clip scraper | Twitch's official Helix API with the owner's free developer app | Needs owner setup |
| Apify Kick clip scraper | none found that is reliable and allowed | Not available; skip Kick for now |
| Apify TikTok scraper | none found that is reliable and allowed | Not available; skip TikTok as a source |
| gpt-image / nano banana pro | `make_thumbnail.py` (Pillow, Anton font, real frames) | Working |
| Composio + Upload-Post posting | Owner uploads files from `out/` by hand after approving | Planned |
| Clipping campaign submission | Owner submits by hand | Planned |

Note: an attempt to use Twitch's internal web API (the one yt-dlp uses) was refused by the
session's permission checker as unauthorized access. Use only the official Helix API.

Network allowed: YouTube (www, i.ytimg), Twitch (www, gql, two clip CDNs), kick.com,
Hugging Face (whisper model download).

## Waiting on the owner

- [ ] **Twitch developer app (free) for step 4:** dev.twitch.tv/console, "Register Your
      Application", category "Application Integration", OAuth redirect `http://localhost`.
      Copy the Client ID (public, fine to share). Then say "twitch app ready". The client
      secret goes only into the secure credential form, never chat.
- [ ] Time zone + preferred day for the weekly outlier rerun (step 2) and daily clip pull (step 4).
- [ ] Record the gameplay listed in `script.md` and share a download link (e.g. an unlisted
      YouTube upload or a cloud-drive link). Video files are too large for git; the agent
      downloads them into the ignored `footage/` folder.
- [ ] Footage source decision (rule 5: credit is not permission).

## Awaiting approval

_(none: nothing has been made from real footage yet)_

## Next run

1. If the Twitch app is ready: build `scripts/grab_clips.py` (Helix Get Clips for
   game "Grand Theft Auto VI", last 24 h, rank by views/hour, keep source links, skip
   cutscenes/endings/exploits), then run steps 5-6 on the day's best clips, then the gauntlet.
2. If footage for `script.md` arrives: cut it, make 3 thumbnails, gauntlet, then ask for approval.
