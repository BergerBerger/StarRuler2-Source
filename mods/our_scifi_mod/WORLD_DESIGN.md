# World Design & Asset Reference — Humans vs Rebels

This document describes how the game works — campaign layer, tactical
battles, resources, bodies, buildings, defenses, fleets, ships, and
research — as a reference for anyone (human or AI) creating art, audio, or
UI assets for it. This is the full target design, not a description of any
one codebase's current feature-completeness. See Section 15 for an honest
status check on what's actually built and playable today versus what's
described here.

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
   Section 4).
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
  research/hyperdrive jumps/stargates can also cost Energy to use.
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
| **Space station/satellite** | 2 | Depends on what's found | Depends on what's found | Not built from scratch by a player directly — found as a derelict and repaired (Section 13), or otherwise claimed. Each one carries **one random bonus**: extra Energy, extra Research, extra Minerals, a free Spaceport, or a batch of ships |

Some systems generate a **planet-and-moon pair** — the moon is a secondary,
weaker body in the same system as its planet, not a separate discovery.

A body produces nothing until owned. The only way to gain ownership,
neutral or enemy, is conquest through combat (Section 9) — there is no
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

## 6. Buildings (economic slots)

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

## 7. Body defenses (separate defense-platform slots)

Every ownable body has a **second, separate set of slots** just for
defenses — distinct from the economic building slots in Section 6. These
don't produce Minerals or Energy; they exist purely to help defend that
body if it's attacked.

| Defense structure | Effect |
| --- | --- |
| **Rocket Battery** | Fires on enemy ships during a battle at this body |
| **Laser** | Direct-fire defensive weapon |
| **Forcefield** | Shields friendly units stationed near it during battle |
| **Disruptor** | Periodically (roughly every 10 seconds) jams enemy units in range, preventing them from moving for a few seconds |

### How defenses factor into a battle
If an enemy attacks a tile where you have a body with defenses (and
possibly a fleet also stationed there), the battle is fought as **your
fleet plus that body's defenses, together, against the attacker** — the
defense platforms aren't a separate fight, they're extra combatants on your
side of the same battlefield. Where you place your fleet on the tile/
battlefield relative to those fixed defenses matters, tying into the
deployment step described in Section 9.

---

## 8. Fleets and armies

- Ships on the same tile can be grouped into an **army** (fleet).
- An army's cap is **50 ships**.
- Armies can be **merged** (combine two friendly armies into one) and move
  together as a single unit once merged.
- An army's movement speed per turn equals its **slowest ship's** speed
  stat (Section 3).
- Every individual ship costs Energy per turn to maintain (Section 4) —
  this is the real limiter on how large a standing military an empire can
  field, separate from the one-time Mineral cost to build the ships in the
  first place.

---

## 9. Conquest and tactical battles

There is one way to take territory: defeat whoever's defending it, then
claim it. There is no diplomacy-based annexation.

**The campaign is turn-based; battles are not.** Only the strategic layer
(Section 3) runs in discrete turns. The moment a battle starts, control
switches to continuous real-time RTS play for the duration of that fight —
there is no "turn" inside a battle, units move and act continuously, the
same as any real-time tactics game.

### Triggering a battle
When two hostile armies come within proximity of each other — governed by
the slower army's per-turn movement range — a battle is triggered. If the
target tile holds a body with defenses (Section 7), those defenses join the
defending side automatically. Both players ready up to begin.

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
  fleet sits in friendly territory (see also the Repair Ship, Section 10,
  which can heal ships *during* a battle rather than waiting for the next
  turn).
- **Damage carries over** if the same (not-yet-fully-repaired) army is
  attacked again by another enemy army before it finishes healing — repairs
  don't reset or protect a fleet from a second engagement.

---

## 10. Ships

There is no in-game ship-design editor; ship classes are fixed per faction,
and — importantly — **the two factions do not have a mirrored roster**.
Humans field a conventional lineup plus several specialists; Rebels field a
deliberately narrower, faster, more unconventional lineup.

### Human roster
| Ship | Tier | Role |
| --- | --- | --- |
| **Small** | Baseline | Cheapest, fastest-to-build hull |
| **Medium** | Baseline | Mid-tier hull |
| **Large** | Baseline | Heaviest baseline hull |
| **Shroud** | Special (research-unlocked) | Defensive specialist |
| **Artillery** | Special (research-unlocked) | Heavy long-range specialist |
| **Repair Ship** *(upgrades into Heavy Repair Frigate)* | Special (research-unlocked) | Support/healing specialist |

### Rebel roster
**Rebels have no Small hull.** Their lightest and only "baseline" combat
ship is the Medium — already the fastest hull in the game — and their
heavy tier is filled entirely by a specialist (Drone Ship) rather than a
plain Large.

| Ship | Tier | Role |
| --- | --- | --- |
| **Medium** *(becomes "Jumper" once researched)* | Baseline | Fast, cheap, only light/medium hull Rebels have |
| **Drone Ship** | Heavy specialist — Rebels' equivalent of Human Artillery | Penetrating-laser gunship that also deploys an automated drone swarm |
| **Suicide Drone** | Light specialist | Small, cheap, expendable kamikaze unit |
| **Capitol** | Flagship | Mobile home base and army carrier |

> **Resolving the "penetrating laser" question**: the original design
> reference explicitly calls out a "Rebel heavy artillery" that "uses a
> penetrating laser" (an attack that passes through its target and keeps
> hitting up to three ships behind it) as a mirror to Human Artillery's
> shrapnel rounds. Later design conversation separately introduced a
> "Drone Ship" with a Drone Swarm ability as the Rebel heavy specialist.
> Resolution used in this document: **they're the same ship.** Drone Ship's
> passive main gun *is* the penetrating laser from the original reference;
> Drone Swarm is its additional activated ability on top of that. This
> keeps the roster from needing a fourth, redundant Rebel hull — flag this
> for confirmation if that's not the intended reading.

### Special abilities — press R, on a cooldown
Most specialist ships get a player-activated ability, triggered with **R**,
on its own cooldown, separate from passive stats:

| Ship | Ability | What it does |
| --- | --- | --- |
| **Shroud** (Human) | *(name TBD)* | An activated shield effect that specifically blocks/negates incoming penetrating attacks for its duration — the hard counter to the Rebel penetrating-laser threat. |
| **Artillery** (Human) | **Rocket Barrage** *(name TBD)* | Fires homing rockets that automatically track and close on enemy targets at high speed. The rockets are their own physical projectile with HP — they can be intercepted/shot down in flight — but their speed and homing make them hard to reliably stop. |
| **Repair Ship / Heavy Repair Frigate** (Human) | **Instant Regenerate** | Immediately restores HP to allied ships in range, on top of (not instead of) its normal continuous repair beam. |
| **Jumper** (Rebel Medium, after research) | **Phase Jump** | Short-range teleport/blink to another point on the *battlefield* — a tactical repositioning tool inside a fight, not a strategic-map ability. Until the relevant tech is researched, this ship is a plain Medium with no R-ability. |
| **Drone Ship** (Rebel) | **Drone Swarm** | Deploys a swarm of drones that appear near the Drone Ship and automatically attack any enemy that comes into range — no manual targeting needed once deployed. Further research increases both how many drones are produced per activation and how many can be active/released at once. |
| **Suicide Drone** (Rebel) | **Kamikaze Split** *(name TBD)* | Splits into two smaller charges that automatically ram into the nearest enemy ships at high speed, dealing a large one-time impact hit and destroying the drone itself. |
| **Capitol** (Rebel) | **Jump** *(strategic-map ability — see Section 10's Capitol entry)* | Not a battle ability — this operates on the turn-based campaign map. |

### Repair Ship → Heavy Repair Frigate (Human)
- **Repair Ship** (base): automatically repairs one allied ship at a time
  during battle — no manual targeting needed, it keeps healing whatever
  ally it's currently locked onto.
- **Heavy Repair Frigate** (research upgrade of the same ship): can repair
  up to **5 ships simultaneously** within range, each via its own beam of
  healing "laser" reaching out to the target. Healing is continuous and
  applies even while the target is actively taking damage — it's a
  real-time race between incoming damage and the frigate's regen, not a
  post-battle-only heal.
- Its R-ability (**Instant Regenerate**) is a burst on top of that
  continuous beam-healing, not a replacement for it.

### Capitol: the moving carrier
The Capitol is best understood as a **mobile aircraft carrier that is also
the Rebel faction's home**:
- It doubles as the Rebels' economic "homeworld" — Rebels have no fixed
  home planet, this ship *is* their home, with its own build slots and its
  own per-turn Minerals/Energy income.
- It can carry and move together with its entire attached army — up to the
  full 50-ship army cap (Section 8) — as a single unit on the strategic map.
- **Jump** (its unique strategic ability, not a battle R-ability): teleports
  the Capitol and its entire attached army a chosen number of hex fields
  across the *strategic* map. Cost scales with both army size and jump
  distance: **1 Energy per ship, per field jumped.** A full 50-ship army
  jumping 1 field costs 50 Energy; jumping 3 fields with the same army costs
  150 Energy. Jump has a **2-turn cooldown**.

### Proposed baseline combat stats (starting point for balance, not final)
The design intent is that no unit should feel strictly better or worse than
its counterpart — Humans trade roster breadth and raw toughness for Rebel
speed, mobility, and automation. A first-pass, internally consistent stat
proposal:

| Ship | Attack | HP | Accuracy | Speed | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Human Small | 1 | 2 | 70% | 3 | Cheap skirmisher |
| Human Medium | 2 | 4 | 75% | 2 | All-rounder |
| Human Large | 4 | 8 | 80% | 1 | Slow tank |
| Human Shroud | 1 | 5 | 70% | 2 | Tanky, low offense — its value is the R-ability, not its guns |
| Human Artillery | 5 (hits up to 3 targets) | 6 | 65% | 1 | Long range; R-ability adds homing rockets on top |
| Human Repair Ship | 0–1 (negligible) | 4 | — | 2 | Non-combatant; value is entirely its healing |
| Rebel Medium / Jumper | 2 | 3 | 65% | 4 | Fastest hull in the game |
| Rebel Drone Ship | 3 (penetrating laser, hits up to 3 in a line) | 7 | 60% | 1 | Plus independent drone-swarm damage once activated |
| Rebel Suicide Drone | 1 (passive) / high one-time impact (R-ability) | 1 | — | 5 | Extremely fragile, very fast, meant to be spent, not fought with |
| Rebel Capitol | Low–moderate (defensive) | Very high (flagship-tier) | — | 1 | Not built to brawl — its value is capacity and Jump, not combat stats |

Rebels have fewer distinct combat hulls than Humans, so each Rebel hull
leans harder into a specific identity — raw speed for the Medium/Jumper,
independent pet/swarm damage for the Drone Ship, pure alpha-strike for the
Suicide Drone — rather than competing stat-for-stat with the wider Human
lineup. This needs real playtesting before being treated as final.

---

## 11. Battle-wide abilities (not tied to a specific ship)

Beyond individual ship R-abilities, the design calls for **empire-level
superweapon abilities** usable during a battle, independent of any one
ship — unlocked through research (Section 12), not built as a unit:

- **Antimatter Bomb** / **Thermonuclear Device** — a large-area, high-impact
  strike usable mid-battle. Given the power level implied, these should be
  scarce: a sensible starting design is a small number of uses per game (or
  a very long cooldown) and a steep Minerals/Energy cost, rather than a
  spammable ability. Exact costs, radius, and damage are unspecified and
  need a dedicated balance pass before implementation.

---

## 12. Research

Research is spent on faction identity and unlocks — not generic economy
scaling. Confirmed unlock categories:

- **Specialist harvesters** (Section 6): unlock bonus-rate Mineral
  extraction on asteroid belts and large-yield Energy harvesting on stars.
- **Special units and upgrades** (Section 10): Shroud, Artillery's homing
  rocket ability, the Repair Ship → Heavy Repair Frigate upgrade, the
  Medium → Jumper conversion, and increased Drone Swarm size/output.
- **Stargates**: build a stargate connecting two chosen points on the
  strategic map; once built, fleets can travel between the two connected
  points directly instead of moving tile-by-tile. A stargate connection
  costs Energy continuously, per round, to stay open/maintained — it's an
  ongoing strategic investment, not a one-time cost.
- **Battle-wide superweapons** (Section 11): Antimatter Bomb / Thermonuclear
  Device.

Both factions keep their own small, separate tech list (not a shared tree),
each research project taking about one turn to complete with adequate
Research Lab support.

---

## 13. Commanders (Admirals)

"Commander" and "Admiral" refer to the same system in this design — every
army/fleet, for either faction, can have one assigned.

- Each faction has its own pool of **10 commanders** (Human commanders only
  lead Human fleets, and vice versa).
- An army/fleet can have **one commander assigned** at a time, chosen from a
  fleet command panel that shows the commander's portrait and exact bonuses
  before assignment.
- Commanders grant bonuses to some combination of Attack, HP, Speed,
  Accuracy, and Rate of Fire — each commander has their own distinct
  strengths, not a generic bonus package.
- Commanders progress through **1 to 5 stars**, scaling their bonuses — this
  should only ever change as the result of an actual in-game progression
  event, never silently.
- In battle, the assigned commander's portrait and name are shown, and
  commanders have their own authored voice lines/taunts they use toward
  each other during a fight.

This system needs 20 total commander portraits/identities (10 per faction)
at final asset scope.

---

## 14. Discoverable content: derelict stations

Scattered through the galaxy are derelict station wrecks the player can
investigate. Choosing to act on one costs a modest amount of Minerals
(example values) and grants exactly one of:

| Choice | Example cost (Minerals) | Result |
| --- | ---: | --- |
| **Salvage** | 5 | A burst of research points |
| **Crew** | 8 | A couple of free light ships (the faction's cheapest combat hull) |
| **Repair** | 15 | Claim the hulk as an owned space station (Section 5) |

---

## 15. Current implementation status (read before assuming a system exists)

This document describes the **full target design**. As of this writing, the
only version of this game that's actually playable is a **real-time**
prototype built as a total-conversion mod of Star Ruler 2 — it does **not**
yet implement the turn structure, the separate tactical battle map, prep
phase, army-vs-army proximity triggers, body defenses, commanders, or
finite per-body Minerals described above. In that current build:

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
- Body defenses (Rocket Battery/Laser/Forcefield/Disruptor), the 50-ship
  army cap, commanders, all ship R-abilities, the Capitol's strategic Jump,
  stargates, battle-wide superweapons, and per-body finite Minerals are not
  implemented. The current build's ship roster is also different and
  faction-symmetric (both factions share a Small/Medium/Large lineup plus
  one faction-exclusive support hull), unlike the asymmetric Human vs.
  Rebel roster described in Section 10.

None of that invalidates this document — it's the direction the full game
is meant to go — but **assets should be built for the design described in
Sections 1–14**, and anyone extending the current codebase should treat the
gaps above as the backlog, not as evidence the design changed.

See `PROJECT_NOTES.md` (same folder) for the engineering-side detail on
that current build.

---

## 16. Visual & asset reference

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
- Stargate structure icon/model (strategic map).

### Battle environments
Since each tactical battle's map reflects the strategic tile it happened
on, at minimum: open space, near-a-star, near-an-asteroid-field, and
near-a-planet/station battlefield backdrops.

### Propulsion, weapons & VFX identity
The two factions should read as different at a glance from engine trails
and weapons fire alone, before a player even sees the hull shape:

- **Humans — combustion/fire-based.** Engines are rough, wild-fire-style
  burning exhaust, not clean energy trails. Damage/destruction effects lean
  into fire: sharp radiating explosion bursts plus billowing, scribbly
  smoke trails on a dying ship.
- **Rebels — ion-thruster/laser-based.** Propulsion reads as a cleaner,
  more energetic ion-drive trail (rather than combustion), and their
  weapons are laser bolts (parallel twin-line beam shots) rather than
  projectile fire. Impact/destruction effects lean into sparks and
  debris at the hit point rather than fire and smoke.

This split should carry through every Human vs. Rebel ship, not just the
big flagships — it's as much a propulsion/engine-FX identity as it is a
hull-design one.

### Ships
Each needs a portrait/icon and an exterior model/silhouette concept. Note
the rosters are **not mirrored** — see Section 10. Concept sketches exist
for the full roster (see `concept_art/` in this folder — add the source
image there under a descriptive filename, e.g.
`concept_art/ship_roster_sketch_01.jpg`, so it can be referenced directly
alongside this text) and describe the following silhouettes and behavior:

**Human roster (from concept sketch):**
- **Small** — a simple small oval/rounded hull; plain straight engine-trail
  dash beneath it, no flourish (baseline ships keep their trail simple).
- **Medium** — a small hook/"C"-shaped hull, open bracket profile.
- **Large** — a blockier "E"-shaped hull: flatter top, a notch cut into the
  profile, visibly bigger than Small/Medium.
- **Shroud** — a diamond/kite-shaped hull with two triangular points, like
  a stylized gem or emblem — reads as a shield/utility unit rather than a
  gun platform. Its sketched effect is a jagged, spiky radiant burst
  beneath it (distinct from the plain baseline trail), tying its visual
  identity to its shield ability rather than to thrust.
- **Artillery** (heavy unit) — a turreted platform: a rectangular base with
  a raised box/turret element on top. Its R-ability (homing rockets) is
  sketched as a separate small rocket shape with its own short exhaust
  trail, distinct from the ship's own engine trail.
- **Repair Ship** — a small hull with a raised antenna/dish protruding from
  the top (the source of its healing beam). Sketched with a dotted-line
  connection reaching toward another small ship shape, and a separate
  "repair ship heals" sketch shows several small connected boxes linked by
  dashes — the visual for the Heavy Repair Frigate's multiple simultaneous
  healing beams reaching out to up to 5 allies at once.
- Fire/smoke reference sketches: a sharp radiating explosion burst, and a
  separate scribbly "smoke" cloud — the two damage/destruction effects to
  build out for Human ships (see Propulsion/VFX note above).

**Rebel roster (from concept sketch):**
- **Medium** — a flat, low rectangular hull with small fin-like
  protrusions; sleeker and flatter than the Human Medium.
- **Capitol Ship** — a large hull made of three joined rectangular
  segments forming one elongated shape, dramatically bigger than any other
  Rebel ship — reads immediately as "carrier-scale," consistent with its
  role as the Rebels' mobile home base.
- **Jumper** — a small hull with a wing/tail fin, sketched with a
  directional arrow beside it emphasizing speed/movement — needs a visual
  "upgraded" tell versus the plain Medium once Phase Jump is researched
  (glowing drive/phase emitters work thematically).
- **Drone Ship** — an elongated hull with a jagged ridge/spine of small
  fins along the top, like a launcher array — reads as a carrier/launcher
  for its drones.
- **Drones** (the ones Drone Swarm deploys) — sketched as a plain, minimal
  small square: deliberately generic and simple, since there are meant to
  be several on screen at once.
- **Suicide Drone** — sketched as a distinct "H"-shaped small hull (two
  prongs joined by a bar) — intentionally different from the plain-square
  swarm Drones above so players don't visually confuse the two "drone"
  concepts.
- Laser/impact reference sketches: a laser bolt (parallel twin-line beam
  with a directional arrow) for weapons fire, and a separate impact sketch
  showing a small ship struck with sparks/debris radiating outward — the
  damage/destruction effect to build out for Rebel ships (sparks/debris,
  not fire/smoke — see Propulsion/VFX note above).
- Capitol (Rebel flagship — visually should read as "a moving aircraft
  carrier / home," the largest, most distinctive hull in the game)

*(Add ship portrait/model images here once provided.)*

### Buildings and defenses
- Economic: Mineral Mine, Energy Harvester (basic), Specialist Asteroid
  Harvester, Specialist Stellar Harvester, Spaceport, Research Lab.
- Defense platforms (visually distinct category from economic buildings):
  Rocket Battery, Laser, Forcefield (needs a shield-bubble visual effect),
  Disruptor (needs a periodic pulse/jam visual effect).

*(Add building/defense icon images here once provided.)*

### Resource icons
- **Minerals** — a gem/ore icon (not a coin, not a hammer/tool icon).
- **Energy** — an energy/bolt-style icon.

### Commanders
- 10 Human commander portraits, 10 Rebel commander portraits, plus a visual
  language for the 1–5 star progression.

### Battle-wide ability icons
- Antimatter Bomb / Thermonuclear Device activation icon and its
  large-area detonation visual effect.

### UI elements
- Empty/filled build-slot icons, and a visually distinct empty/filled
  defense-slot icon set (so players don't confuse the two slot types).
- Ship-build button icon.
- Prep-phase deployment screen chrome (ready button, per-side deployment
  zone coloring).
- In-battle unit portraits (shown per ship, disappear as ships die).
- R-ability icon per specialist ship (Shroud, Artillery, Repair Ship,
  Jumper, Drone Ship, Suicide Drone) plus cooldown-timer treatment.

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
