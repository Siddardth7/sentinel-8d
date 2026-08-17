#!/usr/bin/env python3
"""Selectively download the CiP-DMD light files from the PTW-Darmstadt public share.

Grabs only the 4 small target files per run folder (~430 KB/folder, ~364 MB total)
and never the large *external_sensor_signals.h5 accelerometer files (~51 GB).

Uses the Nextcloud public-share WebDAV endpoint: the share token is the WebDAV
username with an empty password. That avoids HTML-index scraping (fragile) and
needing rclone configured. Resumable: existing non-empty files are skipped.

Usage:
    python scripts/fetch_cip_dmd.py                 # download into data/raw/process_data
    python scripts/fetch_cip_dmd.py --workers 8
    python scripts/fetch_cip_dmd.py --selftest      # offline checks, no network
"""
from __future__ import annotations

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

TOKEN = "5Wv34VRZEXBLsZK"
DAV = "https://cloud.ptw-darmstadt.de/public.php/webdav"
PD = "cylinder_bottom/cnc_milling_machine/process_data"

TARGETS = (
    "frontside_internal_machine_signals.h5",
    "backside_internal_machine_signals.h5",
    "frontside_timestamp_process_pairs.csv",
    "backside_timestamp_process_pairs.csv",
)
# Guard: anything matching this must never be written (the 21-38 MB files we skip).
FORBIDDEN = re.compile(r"external_sensor_signals\.h5$")


def _session() -> requests.Session:
    s = requests.Session()
    s.auth = (TOKEN, "")
    return s


def list_run_folders(s: requests.Session) -> list[str]:
    """PROPFIND the process_data dir (depth 1) and return the 847 run-folder names."""
    r = s.request("PROPFIND", f"{DAV}/{PD}/", headers={"Depth": "1"}, timeout=120)
    r.raise_for_status()
    hrefs = re.findall(r"<d:href>([^<]*)</d:href>", r.text)
    names = []
    for h in hrefs:
        parts = [p for p in h.split("/") if p]
        # entries that live directly under process_data/ and are collections (trailing /)
        if h.endswith("/") and parts and parts[-1] != "process_data" and "process_data" in parts:
            names.append(parts[-1])
    return sorted(names)


def fetch_one(s: requests.Session, folder: str, out_root: Path) -> tuple[str, str]:
    assert not FORBIDDEN.search(folder), folder  # folders never match; belt-and-braces
    dest_dir = out_root / folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    got, skipped, missing = 0, 0, 0
    for name in TARGETS:
        assert not FORBIDDEN.search(name), f"refusing to write large file: {name}"
        dest = dest_dir / name
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            continue
        url = f"{DAV}/{PD}/{folder}/{name}"
        r = s.get(url, timeout=120)
        if r.status_code == 404:
            missing += 1
            continue
        r.raise_for_status()
        dest.write_bytes(r.content)
        got += 1
    return folder, f"got={got} skip={skipped} miss={missing}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/process_data", type=Path)
    ap.add_argument("--workers", default=8, type=int)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    s = _session()
    print("Listing run folders via WebDAV...", flush=True)
    folders = list_run_folders(s)
    print(f"Found {len(folders)} folders. Downloading {len(TARGETS)} files each -> {args.out}")

    errors = []
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, _session(), f, args.out): f for f in folders}
        for fut in as_completed(futs):
            folder = futs[fut]
            try:
                _, summary = fut.result()
                done += 1
                if done % 50 == 0 or done == len(folders):
                    print(f"[{done}/{len(folders)}] {folder}: {summary}", flush=True)
            except Exception as e:  # noqa: BLE001 - report and continue
                errors.append((folder, repr(e)))

    # Verify the skip guard held: no forbidden file made it to disk.
    leaked = [p for p in args.out.rglob("*") if FORBIDDEN.search(p.name)]
    assert not leaked, f"forbidden files written: {leaked[:3]}"

    print(f"\nDone. folders={done}/{len(folders)}, errors={len(errors)}")
    for folder, err in errors[:10]:
        print(f"  ERR {folder}: {err}")
    if errors:
        print("Re-run to retry failures (existing files are skipped).")
    return 1 if errors else 0


def selftest() -> int:
    # URL building and the skip guard, no network.
    assert FORBIDDEN.search("frontside_external_sensor_signals.h5")
    assert FORBIDDEN.search("backside_external_sensor_signals.h5")
    assert not any(FORBIDDEN.search(t) for t in TARGETS)
    xml = (
        "<d:href>/public.php/webdav/cylinder_bottom/cnc_milling_machine/process_data/</d:href>"
        "<d:href>/public.php/webdav/cylinder_bottom/cnc_milling_machine/process_data/100101_x/</d:href>"
        "<d:href>/public.php/webdav/cylinder_bottom/cnc_milling_machine/process_data/100102_y/</d:href>"
    )
    hrefs = re.findall(r"<d:href>([^<]*)</d:href>", xml)
    names = [
        [p for p in h.split("/") if p][-1]
        for h in hrefs
        if h.endswith("/") and [p for p in h.split("/") if p][-1] != "process_data"
    ]
    assert names == ["100101_x", "100102_y"], names
    print("selftest ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
