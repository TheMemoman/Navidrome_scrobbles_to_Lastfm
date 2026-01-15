#!/usr/bin/env python3

import argparse
import sqlite3
import time
from datetime import datetime
import pylast
import sys

# ================= USER CONFIG =================

DB_PATH = "navidrome.db"

START_YEAR = 2015
END_YEAR = 2026

API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
API_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SESSION_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

BATCH_SIZE = 50              # Last.fm limit
DELAY_BETWEEN_BATCHES = 2    # seconds (safe)

# ===============================================


def query_navidrome():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = f"""
    SELECT
        mf.artist,
        mf.title,
        mf.album,
        a.play_date,
        mf.duration
    FROM annotation a
    JOIN media_file mf ON mf.id = a.item_id
    WHERE a.play_count > 0
      AND a.play_date >= '{START_YEAR}-01-01 00:00:00'
      AND a.play_date <  '{END_YEAR}-01-01 00:00:00'
    ORDER BY a.play_date ASC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


def scrobble_rows(rows, resume_from):
    network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        session_key=SESSION_KEY
    )

    total = len(rows)
    uploaded = resume_from
    batch = []

    print(f"Total scrobbles found : {total}")
    print(f"Starting from index  : {resume_from}")
    print("-" * 50)

    for index, row in enumerate(rows):
        if index < resume_from:
            continue

        artist, track, album, play_date, duration = row

        if not play_date:
            continue

        try:
            dt = datetime.fromisoformat(play_date)
        except ValueError:
            print(f"Skipping invalid date: {play_date}")
            continue

        timestamp = int(dt.timestamp())

        batch.append({
            "artist": artist,
            "title": track,
            "album": album,
            "timestamp": timestamp
        })

        if len(batch) == BATCH_SIZE:
            network.scrobble_many(batch)
            uploaded += len(batch)

            print(
                f"Uploaded {uploaded}/{total} "
                f"(last row index: {index})"
            )

            batch.clear()
            time.sleep(DELAY_BETWEEN_BATCHES)

    # Final batch
    if batch:
        network.scrobble_many(batch)
        uploaded += len(batch)
        print(f"Uploaded {uploaded}/{total} (final batch)")

    print("-" * 50)
    print("Scrobbling complete.")
    print(f"Resume with: --resume-from {uploaded}")


def main():
    parser = argparse.ArgumentParser(
        description="Bulk scrobble Navidrome history to Last.fm"
    )
    parser.add_argument(
        "--resume-from",
        type=int,
        default=0,
        help="Resume scrobbling from this row index"
    )

    args = parser.parse_args()

    rows = query_navidrome()

    if not rows:
        print("No scrobbles found. Exiting.")
        sys.exit(0)

    scrobble_rows(rows, resume_from=args.resume_from)


if __name__ == "__main__":
    main()
