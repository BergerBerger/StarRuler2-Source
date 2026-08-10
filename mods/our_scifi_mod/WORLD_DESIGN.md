# World Design & Asset Reference — Humans vs Rebels

This document describes how the game works — art style, campaign layer,
tactical battles, resources, bodies, buildings, defenses, fleets, ships,
and research — as a reference for anyone (human or AI) creating art, audio,
or UI assets for it. This is the full target design, not a description of
any one codebase's current feature-completeness. See Section 16 for an
honest status check on what's actually built and playable today versus
what's described here.

Where a number, cost, or stat below is stated as an example rather than a
locked balance value, it's marked as such — this document is a **rules and
structure reference**, not a final balance spreadsheet.

---

## 1. The pitch

Two factions — **Humans** and **Rebels** — fight over a galaxy on two
connected layers:

1. A **turn-based strategic campaign** on a square-grid galaxy map: explore,
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

The whole game is presented as if it were **drawn by hand in a notebook**
— see Section 2 for the full art direction. That style is treated as a core
part of the design, not a skin applied afterward.

---

## 2. Art direction: notebook doodle style

The entire game is styled as **scribbled hand-drawn doodles on notebook
paper** — this is the visual identity that should inform every asset, not
just a theme for the map.

### The world is a notebook
- The galaxy map **is** a page of grid/graph-paper (a math notebook), and
  the battlefield in a tactical battle is drawn the same way — same
  square-grid paper look, so the two layers feel like one consistent
  sketchbook rather than two different art styles.
- The background of both the strategic map and the battle map has
  hand-drawn stars, and every celestial body (planets, moons, asteroids,
  stars) is rendered as a doodle too — nothing photographic or rendered,
  everything looks like it was drawn with a pen on the page.

### Strength is in motion and impact, not polish
- The core visual appeal is meant to come from **animation and effects**
  that look like a **flip book** — hand-drawn, frame-by-frame motion with
  a raw, slightly-off, charming quality, not smooth vector/3D animation.
- **Shadows** are strong-contrast and hand-drawn (bold hatching/line work),
  not soft gradients.
- **Hit effects** use **comic-book-style action lines** — radiating speed
  lines and impact bursts drawn the way a comic panel would show a hit,
  not a realistic spark/particle effect.
- **Ship destruction** has a specific gag: when a ship is destroyed, tiny
  hand-drawn **stick figures** are sometimes ejected from it (its "crew"
  flying free) before it's gone — a deliberate moment of character and
  humor in an otherwise chaotic explosion, consistent with the notebook-
  doodle tone throughout.

### Faction color and material identity
- **Humans** — metal and **blue** tones; sophisticated, strong, put-together
  designs. (This already matches the in-project Human government color,
  `#3447c7`.)
- **Rebels** — a rusty, patched-up scrapyard look; earthy tones (Mars red,
  rust orange, etc.) rather than clean metal. Ships should read as
  repurposed/salvaged rather than manufactured. (This already matches the
  in-project Rebel government color, `#c73434`, at the red end of that
  earthy palette.)
- Combined with the propulsion/weapons split in Section 11 (Humans =
  fire/combustion, Rebels = ion/laser), color and material alone should be
  enough to tell the two factions apart even in silhouette.

---

## 3. The galaxy map

The galaxy is organized in two tiers: a wide map of **areas** (like
systems), and each area is itself a local **square grid** you enter and
maneuver within.

### Areas
- The galaxy is made of discrete **areas**, connected to their neighbors —
  moving a fleet from one area into an adjacent one is how a player
  actually travels the galaxy.
- **Undiscovered areas show as grey/blank.** An area is only revealed the
  moment a fleet actually enters it — at that point everything inside
  becomes visible all at once (its body/bodies, any fleets present), not
  gradually.
- Each area usually holds one body, occasionally more: a planet, a moon, or
  an asteroid belt (Section 6).
- Map size is configurable (small/medium/large); a larger setting adds more
  areas around the map.
- The two players start on opposite outer edges of the map.

### Inside an area
- Once entered, an area is its own **10×10 grid of square fields**, drawn
  like graph/math-notebook paper (Section 2) — simpler to draw and animate
  than a hex grid, and it directly reinforces the notebook art direction.
- Bodies sit at the **center** of their area, with a fixed footprint:
  - Planet: **3×3 fields**.
  - Moon: **2×2 fields**.
  - Asteroid belt: **3×3 fields** (same footprint as a planet).
- **Ships are tiny by comparison — a single ship fits inside one field**,
  and many ships can occupy the same field without visual crowding, which
  is part of why armies can run up to 50 ships (Section 9).
- Selecting a discovered body shows its output, owner, build slots, and
  structures.

### Movement, engagement, and claiming distance (inside an area)
- Movement speed is spent in **fields per turn**. A tuned baseline: Small
  ships move **5 fields per turn** (an initial pass used 3, but that felt
  too slow to cross a typical 10×10 area in a reasonable number of turns).
- **Triggering a battle**: two hostile armies trigger a battle once they
  close to within **2 empty fields** of each other.
- **Claiming a body**: a fleet must be within **1 field** of the body's
  edge to use the Claim action — see Section 10 for exactly what claiming
  does depending on who (if anyone) already owns the body.

---

## 4. Turn structure

The strategic campaign layer is **turn-based**. Each turn resolves in this
order:

1. Resolve queued construction and ship production.
2. Apply Minerals and Energy income (and subtract Energy upkeep — see
   Section 5).
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

## 5. Resources

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

### Starting conditions
- After picking a faction and a map, both players begin with **50 Minerals
  and 50 Energy**.
- Humans start with **one Small ship** and a home planet named **Eden**.
- Rebels start with their Capitol ship and escorts (Section 11) and no home
  planet at all (Eden's equivalent is the Capitol itself).

### Spending: buildings, ships, and research cost both resources
Queuing a building or ship, or starting a research project, spends **both**
Minerals and Energy together — not Minerals alone. **Energy is typically
the larger of the two costs.** The example costs given elsewhere in this
document (Section 7's building table, etc.) show the Minerals side only;
treat those as illustrative, with an Energy cost on top still to be tuned.

### UI: resource display
The top-left of the HUD always shows both current totals, plus a small
"+" indicator next to each showing the **projected gain for next round** —
so a player can see their income trend before it actually lands, not just
their current balance.

Both resources are always visible in the HUD.

---

## 6. Heavenly bodies

Every discoverable object type can be owned and built on. Each has its own
build-slot count and resource profile:

| Body | Build slots | Minerals | Energy | Notes |
| --- | --- | --- | --- | --- |
| **Planet** | 5 (up to 8 on rare "special" planets) | Finite pool, moderate | Harvestable, moderate | The standard ownable body; occupies a 3×3 block of fields at the center of its area (Section 3). The Human starting planet, Eden, is one of these. |
| **Moon** | 3–4 | Weak | Weak | Found orbiting some planets; occupies a 2×2 block; not worth as much as a planet or asteroid belt |
| **Asteroid belt** | 2–3 | Finite pool, **faster/bonus extraction rate** than a planet | None (Minerals only) | Mineral-specialized; occupies the same 3×3 footprint as a planet; per-round mining bonus makes it the best pure-Minerals body |
| **Star/sun** | Energy-harvester slots only | None | Massive amounts, harvestable | Building a basic harvester works immediately; a **specialist stellar harvester** (bigger yield) requires research to unlock |
| **Space station/satellite** | 2 | Depends on what's found | Depends on what's found | Not built from scratch by a player directly — found as a derelict and repaired (Section 14), or otherwise claimed. Each one carries **one random bonus**: extra Energy, extra Research, extra Minerals, a free Spaceport, or a batch of ships |

Some systems generate a **planet-and-moon pair** — the moon is a secondary,
weaker body in the same system as its planet, not a separate discovery.

A body produces nothing until owned. The only way to gain ownership,
neutral or enemy, is conquest through combat (Section 10) — there is no
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

## 7. Buildings (economic slots)

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
cost is deducted immediately on queuing. Costs above are the Minerals
portion only — every building also costs Energy, usually more than the
Minerals shown (Section 5).

---

## 8. Body defenses (separate defense-platform slots)

Every ownable body has a **second, separate set of slots** just for
defenses — distinct from the economic building slots in Section 7. These
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
deployment step described in Section 10.

---

## 9. Fleets and armies

- Ships on the same tile can be grouped into an **army** (fleet).
- An army's cap is **50 ships**.
- Armies can be **merged** (combine two friendly armies into one) and move
  together as a single unit once merged.
- An army's movement speed per turn equals its **slowest ship's** speed
  stat (Section 4).
- Every individual ship costs Energy per turn to maintain (Section 5) —
  this is the real limiter on how large a standing military an empire can
  field, separate from the one-time Mineral cost to build the ships in the
  first place.

### Fleet UI
- The player's own fleet is shown in the **bottom-right** of the HUD as a
  row of ship slots, one per ship — these can be manually **reordered by
  strength or defense**, which matters for how the fleet lines up during
  the battle prep phase (Section 10).
- A separate, dedicated slot in the same panel holds the fleet's assigned
  **Commander** (Section 14).

---

## 10. Conquest and tactical battles

There is one way to take territory: defeat whoever's defending it, then
claim it. There is no diplomacy-based annexation.

**The campaign is turn-based; battles are not.** Only the strategic layer
(Section 4) runs in discrete turns. The moment a battle starts, control
switches to continuous real-time RTS play for the duration of that fight —
there is no "turn" inside a battle, units move and act continuously, the
same as any real-time tactics game.

### Triggering a battle
Two hostile armies trigger a battle once they close to within **2 empty
fields** of each other (Section 3). If the target holds a body with
defenses (Section 8), those defenses join the defending side automatically.
Both players ready up to begin.

### Claiming a body
Once your fleet is within **1 field** of a body's edge (Section 3), you can
use the Claim action — what happens depends entirely on who (if anyone)
already owns it:

- **Empty/neutral body**: ownership transfers **immediately** — no fighting
  required at all.
- **Enemy-owned body with an active defense platform**: the defense
  platform must be destroyed first, in a full tactical battle (this
  section) — only once it's gone can a claim be made.
- **Enemy-owned body with buildings but no defense platform**: pressing
  Claim doesn't resolve instantly. Each building on the body has its own
  defense value by type — **Mineral Mine / Energy Harvester: 5**,
  **everything else (Spaceport, Research Lab, etc.): 10**. Your fleet's
  strength grinds this down over time (proportional to how strong your
  fleet is), destroying buildings one at a time. Once every building is
  gone, the body can be claimed exactly as if it had always been empty.

An enemy body can therefore be taken two different ways depending on what's
defending it: a straight tactical battle if there's a defense platform, or
a strength-vs-buildings grind (no separate battle screen needed) if there
isn't.

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
- Like the strategic map, the battlefield is drawn as **square-grid
  notebook paper** (Section 2/3) for visual consistency. Movement itself
  stays continuous and real-time, not locked to one ship per cell — ships
  are tiny relative to a square (Section 3), so many can occupy the same
  area of the grid at once. Units occupy real physical space and
  **collide/bounce off each other** rather than freely overlapping or fully
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
  fleet sits in friendly territory (see also the Repair Ship, Section 11,
  which can heal ships *during* a battle rather than waiting for the next
  turn).
- **Damage carries over** if the same (not-yet-fully-repaired) army is
  attacked again by another enemy army before it finishes healing — repairs
  don't reset or protect a fleet from a second engagement.

---

## 11. Ships

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
| **Drone Ship** | Heavy specialist — Rebels' equivalent of Human Artillery | Deploys an automated drone swarm |
| **Suicide Drone** | Light specialist | Small, cheap, expendable kamikaze unit |
| **Capitol** | Flagship | Mobile home base and army carrier |

> **Resolving the "penetrating laser" question**: earlier drafts of this
> document guessed that "penetrating laser" was a trait built into a
> specific Rebel ship (Drone Ship). The project's fuller conversation
> history resolves this more precisely: **Penetrating Lasers is a Rebel
> research tech, not a single ship's weapon.** Once researched, it applies
> to *every* Rebel ship's laser fire — see Section 13's Research section
> for the mechanic. Drone Ship's own gun is a normal laser like any other
> Rebel ship's; it doesn't need a unique passive weapon on top of Drone
> Swarm to justify its identity.

### Special abilities — press R, on a cooldown
Most specialist ships get a player-activated ability, triggered with **R**,
on its own cooldown, separate from passive stats:

| Ship | Ability | What it does |
| --- | --- | --- |
| **Shroud** (Human) | **Shield Field** | Projects a shared shield pool (baseline: **5 shield HP**, **3-field radius**) that any friendly ship inside the radius draws from before taking hull damage. The pool doesn't regenerate on its own — once it's depleted the shield is down until reactivated (**8-second cooldown**). This is the hard counter to the Rebel Penetrating Lasers tech (Section 13): a beam stops the instant it hits a shielded ship. |
| **Artillery** (Human) | **Rocket Barrage** *(name TBD)* | Fires homing rockets that automatically track and close on enemy targets at high speed. The rockets are their own physical projectile with HP — they can be intercepted/shot down in flight — but their speed and homing make them hard to reliably stop. |
| **Repair Ship / Heavy Repair Frigate** (Human) | **Instant Regenerate** | Immediately restores HP to allied ships in range, on top of (not instead of) its normal continuous repair beam. |
| **Jumper** (Rebel Medium, after research) | **Phase Jump** | Short-range teleport/blink to another point on the *battlefield* — a tactical repositioning tool inside a fight, not a strategic-map ability. Until the relevant tech is researched, this ship is a plain Medium with no R-ability. |
| **Drone Ship** (Rebel) | **Drone Swarm** | Deploys a swarm of drones (baseline: **10 drones** per activation) that appear near the Drone Ship and automatically attack any enemy that comes into range — no manual targeting needed once deployed. The drones themselves are individually very weak and fragile (fast, low HP, low per-hit damage — they win through numbers, not toughness). Further research increases both how many drones are produced per activation and how many can be active/released at once. |
| **Suicide Drone** (Rebel) | **Kamikaze Split** *(name TBD)* | Splits into two smaller charges that automatically ram into the nearest enemy ships at high speed, dealing a large one-time impact hit and destroying the drone itself. |
| **Capitol** (Rebel) | **Jump** *(strategic-map ability — see below)* | Not a battle ability — this operates on the turn-based campaign map. |

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
  full 50-ship army cap (Section 9) — as a single unit on the strategic map.
- **Jump** (its unique strategic ability, not a battle R-ability): teleports
  the Capitol and its entire attached army a chosen number of grid squares
  across the *strategic* map. Cost scales with both army size and jump
  distance: **1 Energy per ship, per field jumped.** A full 50-ship army
  jumping 1 field costs 50 Energy; jumping 3 fields with the same army costs
  150 Energy. Jump has a **2-turn cooldown**.

### Proposed baseline combat stats (starting point for balance, not final)
The design intent is that no unit should feel strictly better or worse than
its counterpart — Humans trade roster breadth and raw toughness for Rebel
speed, mobility, and automation. These numbers draw on stats that were
actually tuned and played in an earlier prototype of this game, adapted to
the current roster (not invented from scratch):

**Two different "speed" stats — don't confuse them.** "Battle Speed" below
is a separate, real-time movement/agility rating used only inside a
tactical battle. It has nothing to do with the strategic fields-per-turn
movement from Section 3 (Small ships = 5 fields/turn on the campaign map,
locked) — that stat governs the turn-based campaign layer only.

| Ship | Attack | HP | Accuracy | Rate of Fire | Battle Speed | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Human Small | 4 | 15 | 88% | 1.0/s | 3 | Cheap skirmisher |
| Human Medium | 8 | 30 | 85% | 0.7/s | 2 | All-rounder |
| Human Large | 15 | 60 | 90% | 0.5/s | 1 | Slow tank |
| Human Shroud | 2 | 12 | 70% | 0.45/s | 2 | Weak guns — its value is Shield Field, not its attack |
| Human Artillery | 12 (Shrapnel hits up to 3 targets, reduced falloff) | 35 | 70% | 0.5–0.8/s | 1 | Long range; R-ability adds homing rockets on top of its passive Shrapnel fire |
| Human Repair Ship | 0 (non-combatant) | 15 | — | — | 2 | Value is entirely its healing, not fighting |
| Rebel Medium / Jumper | 10 | 20 | 90% | 0.6/s | 4 | Fastest hull in the game |
| Rebel Drone Ship | 8 | 50 | 85% | 1.6/s | 1 | Fast-firing gun despite being the heavy hull; plus independent drone-swarm damage once activated; gains piercing shots once Penetrating Lasers (Section 13) is researched, same as every other Rebel ship |
| Rebel Suicide Drone | 1 (passive, negligible) / high one-time impact (R-ability) | 1 | — | — | 4 (tied with Jumper, not faster) | Extremely fragile, meant to be spent, not fought with |
| Rebel Capitol | 25 | 100 | 92% | 0.9/s | 1 | Not built to brawl — its value is capacity and Jump, not combat stats |

Rebels have fewer distinct combat hulls than Humans, so each Rebel hull
leans harder into a specific identity — raw speed for the Medium/Jumper,
independent pet/swarm damage for the Drone Ship, pure alpha-strike for the
Suicide Drone — rather than competing stat-for-stat with the wider Human
lineup. This needs real playtesting before being treated as final.

---

## 12. Battle-wide abilities (not tied to a specific ship)

Beyond individual ship R-abilities, the design calls for **empire-level
superweapon abilities** usable during a battle, independent of any one
ship — unlocked through research (Section 13), not built as a unit:

- **Antimatter Bomb** / **Thermonuclear Device** — a large-area, high-impact
  strike usable mid-battle. Given the power level implied, these should be
  scarce: a sensible starting design is a small number of uses per game (or
  a very long cooldown) and a steep Minerals/Energy cost, rather than a
  spammable ability. Exact costs, radius, and damage are unspecified and
  need a dedicated balance pass before implementation.

---

## 13. Research

Research is spent on faction identity and unlocks — not generic economy
scaling. Confirmed unlock categories:

- **Specialist harvesters** (Section 7): unlock bonus-rate Mineral
  extraction on asteroid belts and large-yield Energy harvesting on stars.
- **Special units and upgrades** (Section 11): Shroud, Artillery's homing
  rocket ability, the Repair Ship → Heavy Repair Frigate upgrade, the
  Medium → Jumper conversion, and increased Drone Swarm size/output.
- **Stargates**: build a stargate connecting two chosen points on the
  strategic map; once built, fleets can travel between the two connected
  points directly instead of moving tile-by-tile. A stargate connection
  costs Energy continuously, per round, to stay open/maintained — it's an
  ongoing strategic investment, not a one-time cost.
- **Battle-wide superweapons** (Section 12): Antimatter Bomb / Thermonuclear
  Device.

Both factions keep their own small, separate tech list (not a shared tree),
each research project taking about one turn to complete with adequate
Research Lab support.

### Example tech list (grounded in prototype history)
An earlier prototype of this game had a working, playtested tech tree.
These are good concrete examples of what a real tech list looks like —
adapt names/costs to fit this game's economy rather than copying the exact
old numbers verbatim:

**Human examples:**
| Tech | Effect |
| --- | --- |
| Advanced Extraction | Bonus Minerals/Energy per building |
| Reinforced Plating | +25% HP, fleet-wide |
| Battle AI | +25% accuracy |
| Advanced Railguns | +25% attack |
| Shield Tech | Unlocks the Shroud |
| Artillery Systems | Unlocks Artillery (requires a Spaceport) |
| **Shield Matrix** | Every Human ship gets a small personal shield (baseline: **1 shield HP**) that absorbs one hit before hull HP is touched, doesn't regenerate once spent, and — notably — **also blocks Rebel Penetrating Lasers**, the same as a Shroud's Shield Field does |

**Rebel examples:**
| Tech | Effect |
| --- | --- |
| Warp Drive | +25% thrust/speed |
| Composite Armor | +25% HP, fleet-wide |
| Enhanced Lasers | +25% attack |
| Phase Jump | Unlocks Jumper (the Medium's researched upgrade) |
| Drone Swarm | Unlocks the Drone Ship |
| Capital Construction | Cheaper Capitol-class construction |
| **Penetrating Lasers** | The key Rebel weapons tech: every Rebel ship's laser fire now pierces — full damage to the primary target, then reduced damage to up to **3 additional ships** behind it in a line. Stopped instantly by any shield (Shroud's Shield Field or the Human Shield Matrix tech) — the beam simply stops there instead of passing through. |

**Shared:** a Research Center-type building/tech that lets a body research
two projects at once instead of one.

### Research levels (ships and buildings)
Most ships and buildings aren't a single unlock-or-don't — they upgrade
through numbered **levels** via research, each level taking more turns
than the last:

- **Level 1** — the base stats/effects already described elsewhere in this
  document. No research needed; this is what you have by default once the
  ship/building exists.
- **Level 2** — a meaningful upgrade over Level 1: either a stat boost (a
  proposed baseline: **+25%** to the unit/building's primary stat or
  output) or, for the ships that have one, the point where their
  specialist upgrade actually unlocks (Medium → Jumper, Repair Ship →
  Heavy Repair Frigate both work as "Level 2" outcomes rather than
  separate one-off unlocks). Proposed cost: **2 turns**.
- **Level 3** — a further upgrade on top of Level 2 (another **+25%**, or
  more output from an ability already unlocked — e.g. more drones per
  Drone Swarm activation, more simultaneous heal targets for the Heavy
  Repair Frigate). Proposed cost: **3–4 turns** (deliberately pricier than
  Level 2, since it's the deeper investment).

This reuses upgrades already established elsewhere in this document
(Jumper, Heavy Repair Frigate, Drone Swarm scaling) as the natural Level-2/
Level-3 outcomes of this system, rather than introducing a second, separate
progression track on top. Buildings follow the same pattern — a Level 2
Mineral Mine extracts faster, a Level 2 Spaceport builds ships faster, and
so on. Exact per-level numbers and per-ship/building applicability need a
full balance pass; the three-tier structure and its turn costs are the
starting proposal.

---

## 14. Commanders (Admirals)

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

### Progression
- Commanders gain **XP** (the natural source is participating in battles)
  which accumulates toward their star rank.
- A commander's bonus isn't a single flat stat — it can cover **Speed,
  Cooldown reduction, Defense, Strength (attack), or a combination** of
  these. Each commander has their own specific mix, which is what makes
  picking one for a given fleet an actual decision rather than a flat
  upgrade every commander provides equally.

### Planned, not yet decided: commander special abilities
Beyond passive fleet bonuses, commanders may eventually get their own
battle-activatable special ability — ideas raised include a nuke, a heal,
or something unique per commander — costing **Energy** to trigger mid-
battle. This is a future direction, not a locked decision; which
commanders get which ability, exact costs, and cooldowns are all still
open.

This system needs 20 total commander portraits/identities (10 per faction)
at final asset scope.

---

## 15. Discoverable content: derelict stations

Scattered through the galaxy are derelict station wrecks the player can
investigate. Choosing to act on one costs a modest amount of Minerals
(example values) and grants exactly one of:

| Choice | Example cost (Minerals) | Result |
| --- | ---: | --- |
| **Salvage** | 5 | A burst of research points |
| **Crew** | 8 | A couple of free light ships (the faction's cheapest combat hull) |
| **Repair** | 15 | Claim the hulk as an owned space station (Section 6) |

---

## 16. Current implementation status (read before assuming a system exists)

This document describes the **full target design**. As of this writing, the
only version of this game that's actually playable is a **real-time**
prototype built as a total-conversion mod of Star Ruler 2 — it does **not**
yet implement the notebook-doodle art style, the turn structure, the
separate tactical battle map, prep phase, army-vs-army proximity triggers,
body defenses, commanders, or finite per-body Minerals described above. In
that current build:

- The visual style is Star Ruler 2's own 3D sci-fi rendering, not hand-drawn
  doodles — none of Section 2's art direction is implemented yet.
- Everything happens continuously in real time, not in discrete turns.
- Combat is Star Ruler 2's native continuous space combat — there is no
  separate battle map, no prep phase, and no manual per-unit deployment
  screen.
- The map is Star Ruler 2's native free-form starfield, not a square grid.
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
  Rebel roster described in Section 11.

None of that invalidates this document — it's the direction the full game
is meant to go — but **assets should be built for the design described in
Sections 1–15**, and anyone extending the current codebase should treat the
gaps above as the backlog, not as evidence the design changed.

See `PROJECT_NOTES.md` (same folder) for the engineering-side detail on
that current build.

---

## 17. Visual & asset reference

Reference images should be attached here by category, once provided. See
Section 2 first for the overall art direction (notebook doodle style,
flip-book animation, drawn shadows/comic lines/stick-figure ejection, and
the Human blue-metal vs. Rebel rusty-earthy color split) — everything below
should be built to match that, not as a separate style.

### Faction identity
- **Humans** — metal, blue, sophisticated/strong (Section 2).
- **Rebels** — rusty, patched-up scrapyard, earthy tones (Section 2).

*(Add faction emblem/logo doodle images here once provided.)*

### The galaxy map
- A grey/blank doodle treatment for undiscovered **areas**, and a fully
  revealed square-grid "notebook paper" look once an area is entered — at
  least a few doodled variants (empty space, nebula/asteroid field, near a
  star) for the 10×10 grid inside an area.
- Per-body doodle icons: planet (3×3), moon (2×2), asteroid belt (3×3),
  star, station, black hole — each drawn, not rendered, sized to the field
  footprints in Section 3.
- Stargate structure icon/model (strategic map).

### Battle environments
Since each tactical battle's map reflects the strategic tile it happened
on, at minimum: open space, near-a-star, near-an-asteroid-field, and
near-a-planet/station battlefield backdrops — all on the same square-grid
notebook-paper look as the strategic map (Section 10).

### Propulsion, weapons & VFX identity
The two factions should read as different at a glance from engine trails
and weapons fire alone, before a player even sees the hull shape:

- **Humans — combustion/fire-based.** Engines are rough, wild-fire-style
  burning exhaust, not clean energy trails. Damage/destruction effects lean
  into fire: sharp radiating explosion bursts plus billowing, scribbly
  smoke trails on a dying ship — plus the ejected-stick-figure gag from
  Section 2 on destruction.
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
the rosters are **not mirrored** — see Section 11. Concept sketches exist
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
  build out for Human ships.

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
  not fire/smoke).

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
- Top-left resource readout: current Minerals/Energy plus a small "+"
  next-round-projection indicator for each.
- Bottom-right fleet panel: a row of per-ship slots (reorderable by
  strength/defense) plus one dedicated Commander slot.
- A "Claim" action button/icon, plus a way to visually show a body's
  buildings being ground down (defense value depleting) when claiming an
  enemy body that has no defense platform.
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
