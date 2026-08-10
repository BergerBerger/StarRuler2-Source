# World Design & Asset Reference — Humans vs Rebels (RTS)

This document describes how the game actually works, faction by faction and
system by system, as a reference for anyone (human or AI) creating art,
audio, or UI assets for it. It describes the **RTS version** — a real-time
strategy/4X built on top of Star Ruler 2's engine — not the original Unreal
prototype the concept started from. Where a mechanic differs from a normal
4X or from vanilla Star Ruler 2, that's called out explicitly, since assets
should match what the game actually does, not genre convention.

Every number, name, and cost below is taken directly from the current game
data, not aspirational — if you're building an asset around a specific
value (e.g. "the mine costs 2"), it's accurate as of this writing.

---

## 1. The pitch

Two factions — **Humans** and **Rebels** — fight over a galaxy of star
systems in real time. There is no turn structure, no diplomacy, no hex-grid
ship editor, and no vanilla Star Ruler economy (Influence, native resources,
population). Everything reduces to two resources, one way to take territory
(conquest), a handful of fixed ship classes, and a small per-faction tech
tree. The design goal throughout has been **simplicity and clarity** over
faithfulness to vanilla Star Ruler 2 or to traditional 4X depth — every
system below was deliberately trimmed down from something more complex.

---

## 2. Resources

There are exactly two resources. Nothing else (no Influence, no native
resources like Ore/Water/Gems, no population, no labor-as-a-player-facing-stat).

### Minerals
- A **stockpile**: earned continuously, spent in one-off chunks to build
  buildings and ships.
- Displayed as a bare number (no currency symbol) with a gem/ore icon —
  deliberately *not* a dollar sign or a hammer, since it represents mined
  material, not cash or labor.
- Starting amount: 50 for every empire.

### Energy
- Currently spent on research. The intent (not yet implemented — see
  Section 9) is for Energy to become a **continuous flow** resource:
  uncapped in total, but constantly drained by upkeep (ship maintenance,
  FTL/hyperdrive jumps, building maintenance), so a bigger military or empire
  requires proportionally more Energy production to sustain, not just a
  bigger one-time investment. Minerals stay a bankable stockpile because they
  fund discrete purchases; Energy is meant to behave like a rate you have to
  keep ahead of.
- Starting amount: 50 for every empire.

---

## 3. Heavenly bodies

**Every type of object in space can be owned and built on**: planets,
asteroid belts, stars/suns, and orbital stations. This is a deliberate
departure from vanilla Star Ruler 2, where only planets are ownable. Each
body type has a fixed number of **build slots** and a base income once
owned, before any buildings are added.

| Body | Build slots | Base Minerals /60s | Base Energy /60s | Notes |
| --- | ---: | ---: | ---: | --- |
| Planet (homeworld) | 5 | 2 (fixed) | 2 (fixed) | The Human starting planet only |
| Planet (any other) | 5 | random 2–5 | random 2–5 | Rolled once when first generated, fixed for that planet's life |
| Asteroid belt | 2 | random 5–10 | 0 | Mineral-specialized |
| Star/sun | 1 | 0 | random 10–20 | Energy-specialized; the only body type that can host a Star Harvester |
| Orbital/station | 3 | 0 | 2 (fixed) | Built by the player, or claimed from a repaired derelict (Section 8) |

A body produces nothing until it's owned. Ownership only ever changes hands
through conquest (Section 5) — there is no "settle an empty planet for free"
action.

### Selecting a body
Clicking any owned or conquerable body shows a plain row of small square
buttons right next to the info panel — one square per build slot. This is
**not a popup, not a modal panel, and not a separate menu** — it's meant to
feel like an extension of the selection itself:
- An **empty square** shows a "+" icon. Clicking it opens a small list of
  buildable buildings for that body type.
- A **filled square** shows that building's own icon. Clicking it offers to
  destroy the building.
- If the body has a Spaceport built on it, a separate ship-shaped button
  appears next to the slot squares — this is where ships are queued
  (ships don't occupy a slot; they go into a separate build queue, same as
  vanilla Star Ruler 2's ship construction).

There is intentionally no rendered terrain, biome map, population figure,
or planetary "topology" shown anywhere — the game does not model any of
that, so nothing should be drawn implying it does.

---

## 4. Buildings

Exactly five buildings exist. Nothing else from vanilla Star Ruler 2's
building roster (dozens of economy/defense/ancient-ruin buildings) is
buildable, even though some of that data still technically exists in the
game's files — those are dead leftovers, not part of the design.

| Building | Cost (Minerals) | Effect | Where it can be built |
| --- | ---: | --- | --- |
| **Mineral Mine** | 2 | +2 Minerals /60s | Any body |
| **Energy Harvester** | 2 | +2 Energy /60s | Any body |
| **Spaceport** | 5 | Unlocks ship construction on this body (see Section 6) | Any body |
| **Research Lab** | 5 | Enables/accelerates research (one Lab funds one 45-point project per 60s cycle) | Any body |
| **Star Harvester** | 10 | +20 Energy /60s | **Suns only** — the sole use of a star's single build slot |

All buildings have zero ongoing maintenance cost today. Buildings complete
over a short real-time build duration after being queued (not instant), but
require no player-managed labor or queue-juggling — you place it and it
finishes itself.

---

## 5. Conquest

There is **one way** to take any body, neutral or enemy-owned: **Conquer**.
There is no Colonize, no AutoColonize, no diplomacy-based annexation — those
vanilla Star Ruler 2 systems have been entirely removed from every menu and
keybind.

- Every flagship (see Section 6) has a Conquer ability.
- Target any Planet, Asteroid, Star, or Orbital — your own empire's, a
  neutral one, or an enemy's.
- Channel for **8 real-time seconds** near the target (it cancels if combat
  breaks out nearby). When it completes, ownership of the body transfers to
  you, along with any buildings already on it, intact and immediately
  productive.
- **Enemy-owned bodies with buildings on them cannot be conquered directly.**
  You have to clear the buildings first with **Bombard** (also on every
  flagship): target an enemy body that still has buildings, and it destroys
  one every 3 seconds for as long as you stay on target — this can be done
  mid-combat, unlike Conquer. Once the last building is gone, Bombard
  releases automatically and Conquer becomes available.
- A body that was never owned before (neutral, freshly discovered) has no
  buildings, so Conquer works on it immediately with no Bombard step needed.

This means the flow to take a defended enemy world is: **fight off or avoid
its defenders → Bombard down its buildings → Conquer**. Taking an empty or
undefended world is just **Conquer**.

---

## 6. Ships

There is no in-game ship design editor. Every ship the player can build
comes from a small, fixed roster — players choose from a portrait and name,
never a blueprint screen.

### Flagships (unique per faction, have Leader AI, carry Conquer + Bombard)
| Ship | Faction | Role |
| --- | --- | --- |
| **Scout** | Human | The Human starting flagship. Exploration-oriented. |
| **Capitol** | Rebel | The Rebel starting flagship *and* the Rebels' mobile "homeworld" — see below. |

### Shared support ships (buildable by both factions from a Spaceport)
| Ship | Size class |
| --- | --- |
| **Small Warship** | Smallest hull |
| **Medium Warship** | Mid-size hull |
| **Large Warship** | Largest shared hull |

### Faction-exclusive support ship
| Ship | Faction |
| --- | --- |
| **Capital Ship** | Human — a larger warship beyond the shared roster |

### The Rebel identity: no homeworld
This is the single biggest asymmetry in the game. **Humans start on a
homeworld planet** (fixed 2 Minerals / 2 Energy base income, 5 build slots,
one Scout in orbit). **Rebels have no home planet at all** — their starting
system's would-be homeworld is destroyed outright at game start. Instead,
Rebels start with:
- One **Capitol** ship (their flagship) — this doubles as their mobile base
  of operations, since they have nowhere fixed to return to.
- Two **Small Warships** escorting it.

Both factions start with 50 Minerals, 50 Energy, and four empty asteroid
belts already generated nearby (home system + adjacent systems) ready to be
claimed and mined.

### Building ships
A body needs a **Spaceport** built on it before it can build ships (see
Section 4). Once built, a ship-icon button appears next to that body's slot
squares; clicking it lists the player's available non-obsolete designs and
queues whichever is picked.

---

## 7. Research

Each faction has its own small, fixed research tree — not vanilla Star
Ruler 2's large shared tech web. Both trees currently have **seven
technologies**, each costing a flat **45 research points** and taking about
one 60-second economy cycle to finish with a single Research Lab. Research
is spent on faction identity — combat modifiers and a unique
activatable fleet ability — not economy scaling.

### Human tech tree
| Tech | Effect |
| --- | --- |
| Extraction | Unlocks an advanced-extraction attribute bonus |
| Hull | +25% hit points, fleet-wide |
| Battle AI | +25% weapon tracking, -20% weapon spread |
| Railguns | +25% railgun damage |
| Shields | +50 fleet shield bonus, grants the **Emergency Shields** activatable ability |
| Artillery | +50% railgun range, +10% railgun damage |
| Shield Matrix | An additional +50 fleet shield bonus |

### Rebel tech tree
| Tech | Effect |
| --- | --- |
| Warp Drive | +25% thrust, turn thrust, and hyperdrive speed |
| Hull | +25% hit points, fleet-wide |
| Weapons | +25% beam weapon damage |
| Phase Jump | Grants the **Phase Jump** activatable fleet ability |
| Drone Swarm | +25% support ship capacity |
| Lasers | +20% beam weapon damage, grants the **Weapon Overcharge** activatable ability |
| Capital Construction | -50% build cost and labor cost for Mothership-class hulls |

The pattern is consistent across both trees: most techs are permanent
passive stat multipliers; a couple specifically grant a new
**player-activated, on-cooldown fleet ability** rather than a passive bonus.
Humans lean toward defense/precision (shields, tracking, hull); Rebels lean
toward mobility/offense (speed, phase jumps, beam damage).

---

## 8. Discoverable content: derelict stations

Scattered through the galaxy are **derelict station** anomalies — a wrecked
hulk the player can scan. On investigating one, the player picks exactly one
of three outcomes, each costing a modest amount of Minerals (cashing in a
find isn't free):

| Choice | Cost (Minerals) | Result |
| --- | ---: | --- |
| **Salvage** | 5 | A burst of 400–800 research points |
| **Crew** | 8 | Two free Small Warships |
| **Repair** | 15 | Claim the hulk itself as a new owned station (3 build slots, same as any other orbital) |

---

## 9. Planned, not yet built

These are agreed design directions that haven't been implemented — flagged
here so asset planning can anticipate them, but nothing below should be
treated as final or built against yet.

- **Harvester ships**: a mobile ship type that can extract resources
  directly from an *unclaimed* asteroid or star without conquering it —
  intended to coexist with (not replace) the stationary Mine/Harvester
  buildings, which stay the "settled economy" option for bodies you actually
  own.
- **Finite Minerals**: unclaimed asteroids would hold a limited pool of
  Minerals that harvester ships deplete over time, unlike the current
  buildings, which generate Minerals indefinitely once built.
- **Energy upkeep**: ships, buildings, and FTL/hyperdrive jumps would draw
  continuously from Energy, making the "produce a surplus" framing in
  Section 2 an actual gameplay pressure rather than just an income stat.

---

## 10. Visual & asset reference

This section is where reference images should be attached, organized by
category. For each item, a short description of what it represents and how
it's used in-game is given so an image can be matched to the right context
even before every asset exists.

### Faction identity
- **Humans** — established, settled, defensive character (they have a fixed
  homeworld to protect). Government trait color in-game: blue (`#3447c7`).
- **Rebels** — mobile, scrappy, offensive character (no fixed home, their
  "capital" is a ship that can go anywhere). Government trait color in-game:
  red (`#c73434`).

*(Add faction emblem/logo images here once provided.)*

### Ships
Each entry needs: a portrait/icon (shown in the build menu and ship info
bar in place of a 3D blueprint preview) and, ideally, a simple exterior
silhouette or model concept.

- **Scout** (Human flagship) — starting ship, exploration-flavored, smallest
  flagship hull.
- **Capitol** (Rebel flagship) — the largest, most distinctive hull in the
  game; visually should read as "a home you can fly," since it functions as
  the Rebels' mobile base.
- **Small Warship** (shared) — smallest combat hull.
- **Medium Warship** (shared) — mid-size combat hull.
- **Large Warship** (shared) — largest shared combat hull.
- **Capital Ship** (Human-only) — a large warship above the shared roster.

*(Add ship portrait/model images here once provided.)*

### Buildings
Each entry needs an icon shown as its slot-square sprite in the build UI.

- **Mineral Mine** — extraction/drilling equipment.
- **Energy Harvester** — collector/array equipment.
- **Spaceport** — a small shipyard/launch structure.
- **Research Lab** — a lab/observatory structure.
- **Star Harvester** — a large solar-collector structure, since it's the
  single dedicated building for a star's one slot.

*(Add building icon images here once provided.)*

### Resource icons
- **Minerals** — a gem/ore icon (not a coin, not a hammer/tool icon).
- **Energy** — existing energy/bolt-style icon (unchanged from current
  design).

### UI elements
- Empty build slot: a "+" icon.
- Filled build slot: the icon of whatever's built there.
- Ship-build button: a ship silhouette icon, shown only once a Spaceport
  exists on that body.

### Bodies
- **Planet** — needs a visual distinction between "owned, developed" (slots
  filled) and "neutral/unclaimed," without implying any terrain/biome
  simulation that doesn't exist.
- **Asteroid belt** — visually distinct from a planet; mineral-flavored.
- **Star/sun** — energy-flavored; visually should read as the source of the
  Star Harvester's power.
- **Orbital/station** — both player-built stations and repaired derelict
  hulks use this same visual category.

*(Add body/environment images here once provided.)*

---

## Where this fits alongside other docs

- `PROJECT_NOTES.md` (same folder) is the **engineering** handoff — code
  structure, testing protocol, gotchas. This file is the **design/asset**
  reference. If the two ever disagree on a game-mechanics fact, trust
  whichever was updated more recently, and flag the stale one for a fix.
- The original Unreal-prototype design doc
  (`GAME_DESIGN_SOURCE_OF_TRUTH.md`) predates this RTS build entirely and
  includes systems (hex tile maps, admirals, turn-based combat,
  lobby/matchmaking) that do not apply here. Don't pull mechanics from it
  without checking against this file first.
