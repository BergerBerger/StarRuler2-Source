# Our Sci-Fi Mod — Project Notes / Handoff

This is a total-conversion mod of Star Ruler 2 into a simplified "Humans vs
Rebels" real-time strategy/4X game. It's built on top of SR2's engine/UI (real-time strategic
map, tactical combat, AngelScript modding layer) rather than written from
scratch, so a lot of the design is "take vanilla SR2's systems and strip or
repurpose them" rather than new systems built from zero.

## What we're trying to build

Two factions, Humans and Rebels, fighting over a galaxy with:

- **Two resources only**: Minerals (pays for structures/ships) and Energy
  (pays for research). No native resources (Ore/Water/etc), no Influence,
  no diplomacy, no vanilla tech tree.
- **Every heavenly body type can be owned and built on**: planets,
  asteroid belts, stars/suns, and stations/satellites. Each has build
  slots and its own base income once owned (see table below).
- **Conquest, not diplomacy**: every flagship has one Conquer action for
  neutral and enemy-owned planets, asteroid belts, stars, and stations. It
  channels for 8 real-time seconds, then transfers the body and its buildings
  intact. Player-facing vanilla Colonize and AutoColonize flows are removed.
- **Fixed ship classes** (Small/Medium/Large + faction flagship), not a
  build-your-own hex-editor design system like vanilla SR2. Players never
  see the blueprint editor.
- **Faction-specific research**: each faction has its own small tech list
  (not vanilla's shared tree) that unlocks a passive stat bonus plus a
  "press R, on cooldown" activatable ability per ship.

The fuller rules reference (resource amounts, ship stat tables, turn
structure, admirals, battle modes, etc.) is at
`C:\Users\tolga\AppData\Local\Temp\claude\GAME_DESIGN_SOURCE_OF_TRUTH.md`
on the machine this was developed on — it was originally written for a
separate Unreal prototype of the same game
([BergerBerger/planeten-spiel](https://github.com/BergerBerger/planeten-spiel)),
so treat it as a rules/balance reference, not a literal spec — a lot of it
(hex tile map, admirals, lobby/matchmaking, turn-based combat) doesn't
apply to SR2's architecture and was intentionally not ported.

## Base income per 60 real-time seconds (once owned)

| Body | Minerals | Energy | Notes |
| --- | ---: | ---: | --- |
| Planet (homeworld) | 2 | 2 | Fixed, not random |
| Planet (any other) | random 2-5 | random 2-5 | Rolled once, kept for life of the object |
| Asteroid belt | random 5-10 | 0 | Mineral-specialized |
| Star/sun | 0 | random 10-20 | Energy-specialized |
| Station/satellite | 0 | 2 | Fixed |

This stacks with buildings (Mineral Mine +2, Energy Harvester +2, Research
Lab, Spaceport, StarHarvester +20 on stars). Buildings currently cost 2-10
Minerals each (rescaled down from vanilla's 100-400, which didn't match a
50-Mineral starting economy).

## Current state — what's actually implemented and tested

- Two-faction setup screen (`data/empires/presets.txt`), each with a
  Government trait granting starting ship(s)/energy and a
  faction-specific research tree (`data/research/HumanTech.txt`,
  `RebelTech.txt`).
- Both factions now have the canonical seven-project research branches from
  the prototype, translated to effects that work immediately in SR2's RTS
  engine. Every project costs 45 Research and targets one 60-second cycle with
  one Research Lab. Prototype-only ship unlocks are represented by functional
  fleet effects until dedicated Shroud/Artillery/Jumper/Drone hull assets are
  authored for this engine.
- Humans start on a homeworld planet with one Scout. Rebels start with no
  homeworld — a mobile Capitol ship (`RebelCapitol` trait) plus two Small
  Warships instead.
- Fixed ship designs only (`data/designs/our_presets/` for shared warships,
  `our_human_presets/` and `our_rebel_presets/` for faction ships); the
  interactive blueprint editor UI is hidden/replaced with a portrait+name
  everywhere it used to show (`ShipInfoBar.as`, `ShipPopup.as`).
- Per-body-type base income (table above), wired through normalized surface
  resources so both Minerals and Energy accrue continuously. Vanilla Energy
  tile resources produce `0.5/second`, so values from the old per-turn brief
  must be divided by `ENERGY_RESOURCE_PER_CYCLE (30)` before calling
  `modResource(TR_Energy, ...)`; using the unscaled value is a 30x bug.
- Map icon shows Minerals (preferred) or Energy on any body producing
  either, whether from a building or the base income above
  (`SurfaceComponent.as::updateIcon()`, both `server/` and `shadow/`
  copies — keep them in sync, they're independent implementations).
- Planet, asteroid, star, and station info bars show exact Minerals/Energy
  output per 60 real-time seconds, including passive body income and buildings.
- The planet management overlay is reduced to the buildable surface,
  construction catalog, and Minerals/Energy/Research rates. Vanilla population,
  pressure, loyalty, auto-import, and native-resource level panels are hidden.
- Conquer ability (`data/abilities/our_abilities/ConquerPlanet.txt`) is the
  player's single capture action for neutral and enemy-owned planets,
  asteroids, stars, and stations. It channels for 8 seconds. Context menus,
  the planet info bar, quickbar, and global keyboard commands no longer expose
  the legacy Colonize or AutoColonize paths.
- Native resources fully stripped from galaxy generation. This took
  several tries — see "Gotchas" below if resources start reappearing.
- Win condition patched to "destroy all of the enemy's units" instead of
  vanilla's "enemy owns zero planets" (which would auto-eliminate the
  Rebels, who never own a planet by design, within seconds of any real
  2-empire game).
- Ship and planet right-click menus trimmed of unused vanilla systems:
  support-ship transfers, auto-import leveling, terraforming,
  retrofitting, and the loyalty-siege capture mechanic (duplicated our
  Conquer ability).

## Known gaps / next up

1. **Unreproduced bug report**: at one point the player saw "500 Minerals"
   displayed instead of the expected 50 starting amount. Every automated
   test (including a 4-minute session well past the ~3-minute budget
   cycle) has shown a clean 50 with no unexplained jump. If this recurs, a
   screenshot showing exactly where the number appears would help — it
   might be a display element other than the main resource bar. The opening
   value is now centralized as `STARTING_MINERALS = 50`, and a regression test
   rejects both duplicate initialization and a literal 500-Mineral start.
2. Dedicated SR2 designs and art are still needed for the prototype's Shroud,
   Artillery, Jumper, and Drone Ship unlocks. Their research nodes currently
   grant equivalent live fleet mechanics instead of dead/unusable designs.
3. The computer-player expansion logic still uses SR2's internal colonization
   machinery. Do not disable that server path until the Weasel AI can select a
   conquest-capable flagship, move it into range, channel Conquer, and recover
   from interrupted captures. Player-facing colonization is already removed;
   migrating the AI is the next gameplay-system slice.

## RTS delivery roadmap

1. **Rules foundation (done):** Humans versus Rebels, Minerals plus Energy,
   fixed ship rosters, per-body income, faction research, unit-elimination
   victory, and build slots on every body type.
2. **Conquest enforcement (player complete):** one 8-second Conquer flow and no
   player-facing Colonize shortcuts. AI conquest migration remains.
3. **Faction combat identity:** ship dedicated Shroud, Artillery, Jumper, and
   Drone designs instead of research-effect stand-ins, then balance their
   real-time roles and cooldowns.
4. **Playable-match vertical slice:** teach the AI the two-resource economy and
   Conquer flow, verify a complete Humans-versus-Rebels match, and add bounded
   gameplay smoke coverage for expansion, production, combat, and victory.
5. **Presentation pass:** replace remaining SR2 terminology and screens with
   the game's own HUD, faction feedback, models, icons, audio, and onboarding.

## Testing protocol (important — read before touching tick/loop code)

- Run the fast data tests first:
  `python -m unittest discover -s mods/our_scifi_mod/tests -v`.
- After a Windows x64 build, run
  `mods/our_scifi_mod/tests/run_engine_smoke.ps1`. It uses an isolated
  temporary profile, compiles every AngelScript context, rejects log errors,
  and cleans up after itself.

- Launch with `--quickstart` for fast iteration
  (`Star Ruler 2.exe --quickstart`, run from the repo root so relative
  data paths resolve — launching with the wrong working directory prints
  "Could not open 'data/objects.txt'" and crashes).
- The authoritative log is
  `%UserProfile%\OneDrive\Documents\My Games\Star Ruler 2\log.txt`
  (or wherever "My Games" resolves without OneDrive) — not stdout, the
  game doesn't reliably write there. Clear it before each test run.
- **Before reading the log after any test involving tick/loop changes,
  check memory usage first** (`tasklist` or Task Manager). Normal is
  roughly 700MB-1GB. Multiple GB means a runaway loop — kill the process
  immediately. This caught a real infinite loop earlier in development.
- Compile errors show up in the log as `Error: <file> | Line N` — the
  process usually keeps running in a broken state rather than crashing
  outright, so don't take "it's still running" as proof the compile
  succeeded; check the log.
- Clean up any debug `print()` statements added to `game_start.as` (or
  wherever) after verifying a fix — several were left temporarily during
  this session's debugging and all were removed before committing.

## Repo/branch layout

- `origin` = upstream `BlindMindStudios/StarRuler2-Source` (the original
  open-source SR2 project — never push here).
- This fork (`BergerBerger/StarRuler2-Source`) and `Golddlion`'s personal
  fork both carry the same `our-scifi-mod` branch. Push to whichever
  you're working from; they're not required to stay in sync with each
  other.
- Mod-specific files live under `mods/our_scifi_mod/`, overriding
  `data/` files at the same relative path. Core engine/script behavior
  changes (income formulas, win condition, context menu, etc.) are direct
  edits to the base `scripts/` tree, since AngelScript mod overrides only
  work at the whole-file/whole-data-entry level, not for small in-place
  tweaks to shared engine logic.
