# Our Sci-Fi Mod tests

The fast unit suite validates the resolved base-game/mod data overlay and the
Humans-versus-Rebels fixed ship rosters:

```powershell
python -m unittest discover -s mods/our_scifi_mod/tests -v
```

After building `Non-Steam Release|x64`, run the engine-backed test:

```powershell
./mods/our_scifi_mod/tests/run_engine_smoke.ps1
```

The smoke test compiles all menu, client, server, and shadow AngelScript in a
temporary isolated profile. It rejects engine log errors and cleans up only
the uniquely named profile directory it created.

On a Windows machine with a graphical session, the bounded gameplay smoke test
also verifies map and hull generation without touching the normal player
profile:

```powershell
./mods/our_scifi_mod/tests/run_quickstart_smoke.ps1
```

These tests protect data and initialization invariants; they do not impose a
turn-based game loop. The game remains a real-time strategy simulation.
