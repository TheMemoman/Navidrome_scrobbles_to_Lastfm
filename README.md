# Navidrome_Scrobbles_to_LastFM
A Python script to synchronize your play history (scrobbles) from your Navidrome database to your Last.fm profile.  
This script allows you to bulk scrobble tracks from your Navidrome history to Last.fm for plays that occurred before you enabled scrobbling.  

**Important:** It does **not** sync play counts, because Navidrome only stores the timestamp of the last play, while Last.fm calculates total plays from individual scrobbles.  

The script is intended to be run **once** to import historical plays; after that, regular scrobbling from Navidrome to Last.fm will continue automatically.

## Description

The script connects to your Navidrome SQLite database and retrieves all tracks you’ve played within a configurable date range (`START_YEAR` to `END_YEAR`). Each track is then submitted to Last.fm using the Last.fm API, preserving the original play timestamps.  

It supports **batch processing** and includes a **resume option**, enabling safe handling of large libraries or interrupted uploads. Progress is printed to the console, showing the number of tracks uploaded and any skipped tracks.
in this vein
## How It Works

1. **Query Navidrome Database**  
   The script connects to your SQLite Navidrome database (`DB_PATH`) and queries all tracks with `play_count > 0` in the `annotation` table. Tracks are filtered by `START_YEAR` and `END_YEAR`.

2. **Batch Submission**  
   Tracks are grouped into batches of size `BATCH_SIZE` (default 50, Last.fm limit). Each batch is submitted sequentially, with a short delay (`DELAY_BETWEEN_BATCHES`) between batches to avoid hitting Last.fm rate limits.

3. **Resume Option**  
   If the script is interrupted, you can resume from a specific row index using the `--resume-from` argument, so previously scrobbled tracks are not duplicated.

4. **Error Handling**  
   Tracks with invalid timestamps are skipped, and progress is logged to the console. The script ensures that scrobbles are submitted safely without stopping for minor errors.

## Configure the following variables

| Name                   | Description                                                                                     | Suggested Value                     |
|------------------------|-------------------------------------------------------------------------------------------------|------------------------------------|
| `DB_PATH`              | Path to your Navidrome SQLite database                                                          | `/path/to/navidrome.db`            |
| `API_KEY`              | Your Last.fm API key (see [Last.fm API docs](https://www.last.fm/api/authentication))          | `xxxxxxxxxxxxxxxxxxx`               |
| `API_SECRET`           | Your Last.fm API secret (see [Last.fm API docs](https://www.last.fm/api/authentication))       | `xxxxxxxxxxxxxxxx`                  |
| `SESSION_KEY`          | Your Last.fm session key (from authentication)                                                 | `xxxxxxxxx`                         |
| `START_YEAR`           | Starting year to include scrobbles                                                              | `2015`                              |
| `END_YEAR`             | Ending year to include scrobbles                                                                | `2026`                              |

## Execute the script

1. Create a virtual environment and install `pylast`:

```bash
python3 -m venv ~/navidrome_lastfm_venv
source ~/navidrome_lastfm_venv/bin/activate
pip install --upgrade pip
pip install pylast
```

2. Run the script from the virtual environment:

```bash
python scrobbles_lastfm.py
```

3. To resume an interrupted run, provide the --resume-from argument:

```bash
python scrobbles_lastfm.py --resume-from 100
```
