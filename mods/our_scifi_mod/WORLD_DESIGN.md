# World Design & Asset Reference — Humans vs Rebels

This document describes how the game works — campaign layer, tactical
battles, resources, bodies, buildings, fleets, ships, and research — as a
reference for anyone (human or AI) creating art, audio, or UI assets for it.
This is the full target design, not a description of any one codebase's
current feature-completeness. See Section 12 for an honest status check on
what's actually built and playable today versus what's described here.

Where a number, cost, or stat below is stated as an example rather than a
locked balance value, it's marked as such — this document is a **rules and
structure reference**, not a final balance spreadsheet.

---

## 1. The pitch

Two factions — **Humans** and **Rebels** — fight over a galaxy on two
connected layers:

1. A **turn-based strategic campaign** on a hexagonal galaxy map: explore,
   claim territory, build, research, and move fleets.
2. A **tactical battle layer**: when opposing armies meet, play shifts to a
   separate battle map for that engagement, in the spirit of *Total War:
   Three Kingdoms* — armies deploy, then fight it out with individually
   commanded units on a battlefield that reflects the environment they met
   in.

There is no diplomacy and no ship-blueprint editor. Ship classes are fixed
per faction. Everything else — resources, territory, tech — is deliberately
kept simple compared to a traditional 4X: two resources, one way to take
territory (conquest through combat), and a small per-faction tech tree.

---

## 2. The galaxy map

- The galaxy is a **hexagonal map made of hexagons** — the overall map shape
  is a hexagon, and every individual tile on it is also a hexagon.
- Map size is configurable (small/medium/large); a larger setting adds
  another ring of hex tiles around the map.
- The two players start on opposite outer edges of the map.
- **Fog of war** covers undiscovered territory. A tile is either
  undiscovered, discovered (known but not currently visible), or currently
  visible — nothing about a hidden tile (contents, fleets, ownership) should
  ever be shown to a player who hasn't earned that visibility.
- **A single hex can contain multiple objects**: one planet, or two planets,
  or an asteroid belt, or a black hole, etc. — hexes are not restricted to
  exactly one discoverable thing.
- Selecting a discovered object shows its output, owner, build slots, and
  structures.

---

## 3. Turn structure

The strategic campaign layer is **turn-based**. Each turn resolves in this
order:

1. Resolve queued construction and ship production.
2. Apply Minerals and Energy income (and subtract Energy upkeep — see
   Section 6).
3. Advance research.
4. Heal/repair fleets sitting in friendly territory.
5. Reset each unit's movement allowance for the new turn.
6. Players (or the CPU) act: move fleets, explore, claim, build, queue
   research, form/merge fleets, and initiate engagements.
7. End turn.

A fleet's movement allowance per turn is capped by its **slowest ship's
speed stat** — the whole army only moves as fast as its slowest member.
Movement allowance is spent, not banked; a unit can't save up unused
movement from a previous turn or be issued multiple move commands to exceed
its per-turn allowance.

---

## 4. Resources

Exactly two resources exist — no Influence, no native resources (Ore/Water/
Gems/etc.), no population or labor as a player-facing stat.

### Minerals
- Pays for structures and ships.
- **Finite per body.** Every mineral-producing body (planets, asteroid
  belts) holds a limited pool; mining it down is possible, unlike Energy.
  Once a body's pool is exhausted, its Mineral output drops off — this is a
  real constraint on how long a single claimed body keeps paying off, not
  an infinite tap.
- Spent in one-off amounts on buildings and ships (not a continuous drain).

### Energy
- Pays for research **and** is the upkeep resource for your military and
  economy: every ship costs Energy per turn to maintain, and abilities/
  research/hyperdrive jumps can also cost Energy to use.
- **Not finite** — a body that can produce Energy can always be harvested
  for more of it (subject to which buildings/research you've unlocked
  there). The limiting factor for Energy isn't "running out," it's whether
  your production stays *ahead* of your total upkeep.
- **Worked example**: if your empire produces 10 Energy per round and you
  have 5 Small ships, each costing 1 Energy/round in upkeep, your total
  upkeep is 5 — so your *net* Energy gain that round is 10 − 5 = 5, not 10.
  Add more ships (or activate more Energy-costing abilities) than your
  production can support, and your net goes to zero or negative — Energy
  is simultaneously your currency, your research fuel, and the hard cap on
  how large a fleet you can actually sustain.

Both resources are always visible in the HUD.

---

## 5. Heavenly bodies

Every discoverable object type can be owned and built on. Each has its own
build-slot count and resource profile:

| Body | Build slots | Minerals | Energy | Notes |
| --- | --- | --- | --- | --- |
| **Planet** | 5 (up to 8 on rare "special" planets) | Finite pool, moderate | Harvestable, moderate | The standard ownable body |
| **Moon** | 3–4 | Weak | Weak | Found orbiting some planets; not worth as much as a planet or asteroid belt |
| **Asteroid belt** | 2–3 | Finite pool, **faster/bonus extraction rate** than a planet | None (Minerals only) | Mineral-specialized; per-round mining bonus makes it the best pure-Minerals body |
| **Star/sun** | Energy-harvester slots only | None | Massive amounts, harvestable | Building a basic harvester works immediately; a **specialist stellar harvester** (bigger yield) requires research to unlock |
| **Space station/satellite** | 2 | Depends on what's found | Depends on what's found | Not built from scratch by a player directly — found as a derelict and repaired (Section 10), or otherwise claimed. Each one carries **one random bonus**: extra Energy, extra Research, extra Minerals, a free Spaceport, or a batch of ships |

Some systems generate a **planet-and-moon pair** — the moon is a secondary,
weaker body in the same system as its planet, not a separate discovery.

A body produces nothing until owned. The only way to gain ownership,
neutral or enemy, is conquest through combat (Section 8) — there is no
free/instant "settle an empty planet" action.

### Selecting a body
Clicking an owned or claimable body shows its build slots as small square
buttons directly next to its info panel — not a popup or separate menu.
- An **empty square** shows a "+" — click it to choose what to build there.
- A **filled square** shows that building's icon — click it to destroy it.
- A body with a Spaceport gets an extra ship-shaped button for queuing
  ship production (ships go into a build queue, they don't occupy a slot).

No terrain, biome map, or population figure is shown for any body — none of
that is modeled, so nothing should visually imply it exists.

---

## 6. Buildings

| Building | Cost (Minerals, example) | Effect | Buildable on |
| --- | ---: | --- | --- |
| **Mineral Mine** | 2 | Extracts from the body's finite Mineral pool | Planet, Moon, Asteroid belt |
| **Energy Harvester** | 2 | Harvests Energy (basic rate) | Any body that can produce Energy |
| **Specialist Asteroid Harvester** | *research-gated* | Bonus-rate Mineral extraction on an asteroid belt | Asteroid belt only, after the relevant research |
| **Specialist Stellar Harvester** | *research-gated* | Large-yield Energy harvesting from a star | Star only, after the relevant research |
| **Spaceport** | 5 | Unlocks ship construction on this body | Any body |
| **Research Lab** | 5 | Enables/funds research | Any body |

The "specialist" harvesters are deliberately gated behind research rather
than available from turn one — they represent an economic tech investment,
not a starting option. Buildings finish a turn after being queued; their
cost is deducted immediately on queuing.

---

## 7. Fleets and armies

- Ships on the same tile can be grouped into an **army** (fleet).
- An army's cap is **21 ships**.
- Armies can be **merged** (combine two friendly armies into one) and move
  together as a single unit once merged.
- An army's movement speed per turn equals its **slowest ship's** speed
  stat (Section 3).
- Every individual ship costs Energy per turn to maintain (Section 4) —
  this is the real limiter on how large a standing military an empire can
  field, separate from the one-time Mineral cost to build the ships in the
  first place.

---

## 8. Conquest and tactical battles

There is one way to take territory: defeat whoever's defending it, then
claim it. There is no diplomacy-based annexation.

### Triggering a battle
When two hostile armies come within proximity of each other — governed by
the slower army's per-turn movement range — a battle is triggered. Both
players ready up to begin.

### Prep phase
Before the fight starts, there's a **one-minute deployment phase**:
- Each player places their own ships anywhere on their own side of the
  battlefield.
- When a player is satisfied with their placement, they press **Ready**.
- Once **both** players have pressed Ready, the battle begins.

### The battle itself
- The battle takes place on a **separate battle map**, generated to reflect
  the environment of the strategic tile the encounter happened in (e.g. a
  battle near a star looks different from one in open space or near an
  asteroid field) — assets need to support multiple battlefield
  backdrops/environments for this reason.
- The battlefield is an **open map, not a hex grid** — ships aren't
  confined to one-hex-per-unit. Units occupy real physical space and
  **collide/bounce off each other** rather than freely overlapping or
  stacking.
- **Each unit can be commanded individually** — select one or many ships
  and give them move/attack orders independently, the way a real-time
  tactics game works, not by giving one order to an entire army at once.
- The battle ends when **every unit on one side's battlefield force is
  destroyed**.

### After the battle
- Surviving ships return to the strategic map with whatever damage they
  took.
- Damage is **healed/repaired starting the turn after the battle** while a
  fleet sits in friendly territory.
- **Damage carries over** if the same (not-yet-fully-repaired) army is
  attacked again by another enemy army before it finishes healing — repairs
  don't reset or protect a fleet from a second engagement.

---

## 9. Ships

There is no in-game ship-design editor; ship classes are fixed per faction.
The baseline roster, from the original design reference (exact numbers are
example balance data, not locked):

### Baseline classes (every faction has its own version)
| Class | Role |
| --- | --- |
| **Small** | Cheapest, fastest-to-build hull |
| **Medium** | Mid-tier hull |
| **Large** | Heaviest baseline hull |

**Human** baseline stats (example): Small (Attack 1 / HP 2 / Speed 1 /
Range 1), Medium (2 / 3 / 2 / 2), Large (5 / 7 / 1 / 3). Human identity:
tougher ships, shields, measured firepower.

**Rebel** baseline stats (example): Small (1 / 1 / 3 / 1), Medium (2 / 2 /
2 / 2), Large (3 / 3 / 2 / 3). Rebel identity: weaker individual hulls but
faster, more accurate/higher fire-rate potential, and penetrating laser
weapons.

### Capitol (Rebel-exclusive flagship)
The Rebels' mobile home base, not just a ship:
- Doubles as the Rebel faction's economic "homeworld" — Rebels have no
  fixed home planet, this ship *is* their home.
- Has its own build slots (baseline 3), produces its own Minerals and
  Energy per turn, and moves across the map at its own turn-speed like any
  other unit.
- Carries an internal **bay** that stores extra ships (baseline capacity:
  10 Small, 5 Medium, 3 Large) — stored ships auto-deploy alongside the
  Capitol into a battle, or can be released onto the strategic map as their
  own independent army.

### Special researched units
Two additional unit types are unlocked through research rather than
available from the start:

- **Shroud** — a defensive specialist unit. Its shields specifically
  counter the Rebel penetrating-laser attack (a Shroud's shield stops the
  penetration effect that would otherwise hit multiple ships in a line).
- **Artillery** — a heavy long-range unit that **both factions get their
  own version of**, with different attack behavior per faction: the Human
  Artillery fires shrapnel rounds (a multi-hit attack with its own accuracy
  handling); the Rebel Artillery fires a penetrating laser (hits through
  its target into up to three ships standing behind it).

> **Note on "Jumper" and "Drone" naming**: internal work on this project has
> used the working names *Jumper* (tied to a Rebel "Phase Jump" mobility
> ability) and *Drone*/"Drone Swarm" (tied to a Rebel support-capacity
> bonus) as thematically Rebel-flavored unlocks. These aren't separately
> named ship types in the original canonical design reference — that
> document only explicitly names **Shroud** and **Artillery** as special
> researched units. Treat Jumper/Drone as working names for Rebel
> mobility/swarm-flavored tech, not confirmed distinct hull types, until a
> firm decision is made.

---

## 10. Admirals

- Each faction has its own pool of **10 admirals** (Human admirals only
  lead Human fleets, and vice versa).
- An army/fleet can have **one admiral assigned** at a time, chosen from a
  fleet command panel that shows the admiral's portrait and exact bonuses
  before assignment.
- Admirals grant bonuses to some combination of Attack, HP, Speed, Accuracy,
  and Rate of Fire.
- Admirals progress through **1 to 5 stars**, scaling their bonuses — this
  should only ever change as the result of an actual in-game progression
  event, never silently.
- In battle, the assigned admiral's portrait and name are shown, and
  admirals have their own authored voice lines/taunts they use toward each
  other during a fight.

This system needs 20 total admiral portraits/identities (10 per faction) at
final asset scope.

---

## 11. Discoverable content: derelict stations

Scattered through the galaxy are derelict station wrecks the player can
investigate. Choosing to act on one costs a modest amount of Minerals
(example values) and grants exactly one of:

| Choice | Example cost (Minerals) | Result |
| --- | ---: | --- |
| **Salvage** | 5 | A burst of research points |
| **Crew** | 8 | A couple of free Small ships |
| **Repair** | 15 | Claim the hulk as an owned space station (Section 5) |

---

## 12. Current implementation status (read before assuming a system exists)

This document describes the **full target design**. As of this writing, the
only version of this game that's actually playable is a **real-time**
prototype built as a total-conversion mod of Star Ruler 2 — it does **not**
yet implement the turn structure, the separate tactical battle map, prep
phase, army-vs-army proximity triggers, admirals, or finite per-body
Minerals described above. In that current build:

- Everything happens continuously in real time, not in discrete turns.
- Combat is Star Ruler 2's native continuous space combat — there is no
  separate battle map, no prep phase, and no manual per-unit deployment
  screen.
- Minerals and Energy are both produced indefinitely by buildings once
  built (no finite per-body pool yet, no Energy upkeep yet).
- Conquest is a single channeled "Conquer" action (8 real-time seconds)
  instead of a turn-based combat-then-claim sequence, and enemy-owned
  bodies must have their buildings destroyed first via a separate "Bombard"
  action.
- Fleet cap, admirals, the Shroud/Artillery special units, and per-body
  finite Minerals are not implemented.

None of that invalidates this document — it's the direction the full game
is meant to go — but **assets should be built for the design described in
Sections 1–11**, and anyone extending the current codebase should treat the
gaps above as the backlog, not as evidence the design changed.

See `PROJECT_NOTES.md` (same folder) for the engineering-side detail on
that current build.

---

## 13. Visual & asset reference

Reference images should be attached here by category, once provided.

### Faction identity
- **Humans** — established, defensive, "protecting a home" character.
- **Rebels** — mobile, scrappy, "home is a ship" character.

*(Add faction emblem/logo images here once provided.)*

### The galaxy map
- Hex tile art, at least a few variants (empty space, nebula/asteroid
  field, near a star) since the map is entirely hex-based.
- Fog-of-war visual treatment for undiscovered vs. discovered-but-not-visible
  tiles.
- Per-body map icons: planet, moon, asteroid belt, star, station, black
  hole.

### Battle environments
Since each tactical battle's map reflects the strategic tile it happened
on, at minimum: open space, near-a-star, near-an-asteroid-field, and
near-a-planet/station battlefield backdrops.

### Ships
Each needs a portrait/icon and an exterior model/silhouette concept:
- Human Small / Medium / Large
- Rebel Small / Medium / Large
- Capitol (Rebel flagship + mobile home)
- Shroud (special defensive unit)
- Artillery — Human and Rebel versions look different given their
  different firing behavior (shrapnel vs. penetrating laser)

*(Add ship portrait/model images here once provided.)*

### Buildings
- Mineral Mine, Energy Harvester (basic), Specialist Asteroid Harvester,
  Specialist Stellar Harvester, Spaceport, Research Lab.

*(Add building icon images here once provided.)*

### Resource icons
- **Minerals** — a gem/ore icon (not a coin, not a hammer/tool icon).
- **Energy** — an energy/bolt-style icon.

### Admirals
- 10 Human admiral portraits, 10 Rebel admiral portraits, plus a visual
  language for the 1–5 star progression.

### UI elements
- Empty/filled build slot icons.
- Ship-build button icon.
- Prep-phase deployment screen chrome (ready button, per-side deployment
  zone coloring).
- In-battle unit portraits (shown per ship, disappear as ships die).

*(Add all image references here once provided.)*

---

## Where this fits alongside other docs

- `PROJECT_NOTES.md` (same folder) is the **engineering** handoff for the
  current real-time Star Ruler 2 prototype specifically — code structure,
  testing protocol, gotchas.
- This file is the **full design/asset** reference — build assets against
  this document, not against whatever subset happens to be implemented in
  any one codebase at a given time.
- The canonical written source for the mechanics in this document is
  `GAME_DESIGN_SOURCE_OF_TRUTH.md` in the `BergerBerger/planet-game`
  GitHub repository. Where this file and that one differ, the newest
  explicit design instruction wins, per that document's own stated rule.
