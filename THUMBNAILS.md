# THUMBNAILS.md: what repeats in the outliers

Source: `data/outliers.csv` (2026-11-21 run). 119 GTA outlier videos (>=3x their channel's
median views) from 28 of 35 approved channels. Thumbnails studied: the top 48 long-form
outliers (`data/thumbs/`). These are observations from one snapshot taken the week of
GTA 6's launch; launch-week interest may inflate "first look" formats. Re-check after the weekly rerun.

## Thumbnail patterns

Ranked by how often they appear in the 48 studied.

1. **Split-screen comparison (~15 of 48).** Two halves, GTA 6 vs GTA 5/4/RDR2/Vice City,
   same shot framed the same way. A red-white "VS" in the seam, each game's logo in its
   half. The compared detail is circled or arrowed (tyre, push animation, NPC).
2. **Official logo as a design element (~30 of 48).** The pink/purple "VI" or "grand theft
   auto" wordmark sits in a corner. It tells you the game at a glance without text.
3. **One big face (~20 of 48).** Either a GTA character (Lucia, Jason) looking into the
   frame with a strong expression, or the creator with a shocked open mouth on the right
   third. Faces are large: roughly a third to half the frame height.
4. **1-3 huge words (~20 of 48).** Heavy condensed sans, yellow or white with a black
   outline/shadow: "EVERYTHING", "DAY 1", "BEFORE / AFTER", "SECRET COFFIN", "200+ THINGS".
   Rarely more than 4 words. Text and title never repeat each other word for word.
5. **Money/number bait (~8 of 48).** Big green "+$1,100,000" or "$0 -> $7,000,000" with a
   red arrow between a before/after pair. FPS tests use a big "FPS: 24" label.
6. **The map (~5 of 48).** The Leonida map in bright tropical colors with a few place labels
   ("Vice City", "Port Gellhorn") and a route line ("40 MIN DRIVE").
7. **One red arrow or circle** pointing at the payoff. Almost every non-face thumbnail has one.
8. **Saturation and light.** Bright daylight, teal water, pink sky; high contrast. Very few
   dark or night thumbnails among the outliers.

What's absent: busy collages, small text, long sentences, dark moody frames, and
thumbnails without a clear single subject.

## Title patterns

From all 119 outlier titles. Numbers are counts from this snapshot, not general rules.

- Length: median 43 characters, 9 words. Short enough to show in full on a phone.
- 55% have at least one ALL-CAPS word for emphasis ("CRAZY", "NEED", "INSANE", "ULTIMATE").
- 31% have a number besides the game number; 11% start with one ("15 THINGS...", "200+ THINGS...").
- 18% are comparisons ("GTA 6 VS GTA 5 (CAR PHYSICS COMPARISON)").
- 21% use a parenthetical qualifier: "(ULTIMATE COMPARISON)", "(No Spoilers)", "(2026)".
- Top words: comparison, things, first, gameplay, details, know, need, best, ultimate,
  everything, graphics, money, guide, before, secret, police, impossible.
- Recurring frames:
  - "N THINGS You NEED To Know/Do Before/On Day 1 in GTA 6"
  - "GTA 6 VS GTA 5 (<detail> COMPARISON)"
  - "The GTA 6 Map Makes No Sense" / "The Entire GTA 6 Map Explained"
  - "I Played/Tried <challenge> in GTA 6" (first person, often with 😱)
  - "How to Make MILLIONS <method> in GTA Online (2026)"

## Rules for our thumbnails (derived)

- One subject, one idea. The payoff frame from our own footage is the background.
- 1-3 words, max 4, in a heavy condensed font, yellow or white with a thick black stroke.
  Never repeat the title.
- Add one red arrow or circle on the payoff.
- Use the VI wordmark style only as a small corner badge (the logo is Rockstar's trademark,
  so don't make it the main element).
- Comparisons: a clean vertical split with a "VS" in the seam, the same angle on both sides.
- Bright, saturated, daylight frames. Check legibility at 168x94 px (phone search size).

## Free toolchain (replaces gpt-image / nano banana pro)

`scripts/make_thumbnail.py`: picks a frame from our footage, crops to 1280x720, boosts
saturation and contrast, and adds 1-3 words with a stroke plus an optional arrow or circle.
The output then goes through the gauntlet (RULES.md rule 2).
