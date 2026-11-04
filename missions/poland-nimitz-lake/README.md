# Poland · Forrestal Lake

A standalone multiplayer custom-room mission for the normal Poland ground map.
It places `us_aircraftcarrier_forrestal_ai`—the largest U.S. carrier available
in the current live client—stationary in the central lake, on Team A. It has sixteen
player slots per team, ground and air spawns for both teams, and a Team A
carrier-takeoff spawn.

Use **Custom Battles → Create Session → Missions by URL** and paste the raw URL
of [`poland-nimitz-lake.blk`](poland-nimitz-lake.blk). It is independent of all
Nuclear Escalation mission files.

Rebuild after editing its generator:

```sh
python3 tools/build_poland_nimitz_lake.py
```
