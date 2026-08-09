# Game Vision: the 15-30 Minute Notebook RTS

This file is the product boundary for the playable alpha. When an older board
game rule, Star Ruler 2 feature, or prototype note conflicts with it, this file
wins until the team deliberately changes it.

## The promise

A hand-drawn real-time space duel that looks like two people sketched a board
game into a notebook, is understandable during the first match, and always
ends within 30 minutes.

## Alpha rules

- One Human player versus one Rebel player or AI.
- Real time, with pausing available for testing and accessibility only.
- One mirrored ten-system Dumbbell map. Both players can read the middle as the
  natural conflict point.
- Two resources: Minerals build structures and ships; Energy drives research.
- Five structures at most: Mine, Energy Harvester, Research Lab, Spaceport,
  and the star-only Star Harvester.
- Fixed ship classes. There is no ship editor.
- Two capture verbs: Conquer an undefended body or Bombard its defenses.
- Four faction upgrades. Each should finish in about 40 seconds with one lab.
- One victory: remove the opposing military. At 30 minutes the existing point
  score resolves the match instead of allowing an endless stalemate.

## Expected match rhythm

| Time | Player experience |
| --- | --- |
| 0-3 minutes | Read the map, place the first economy building, move the starting fleet. |
| 3-10 minutes | Claim nearby bodies, build a Spaceport, choose the first upgrade. |
| 10-20 minutes | Produce fleets, contest the centre, attack exposed production. |
| 20-30 minutes | Commit to the decisive fight; elimination or the time cap ends the match. |

The complete player verb set is select, move/attack, build, produce, research,
Conquer, and Bombard. A new screen or mechanic must justify itself by making
one of those verbs clearer.

## Keep, cut, postpone

| Keep for alpha | Cut from alpha | Postpone until the duel is fun |
| --- | --- | --- |
| Humans and Rebels | Diplomacy, Influence, senate, cards | Admirals and campaign |
| Minerals and Energy | Anomalies, artifacts, remnants, pirates | Dedicated Shroud, Artillery, Jumper, Drone hulls |
| Fixed ships and five buildings | Population, loyalty, pressure, native resources | Multiplayer lobby and matchmaking |
| Four upgrades per faction | Civilian trade, terraforming, ship editor | More maps, factions, upgrades, and victory modes |
| Conquer and Bombard | Random events and secret projects | Cosmetic depth after the notebook language works |
| Elimination plus 30-minute cap | Huge procedural galaxies and alternate victories | Full AI migration from internal colonization to Conquer |

## Visual language

The game should feel drawn, not rendered:

- warm off-white notebook or graph paper behind the play space and panels;
- black or dark-blue ink outlines with visibly imperfect strokes;
- blue pencil/ink accents for Humans and red accents for Rebels;
- simple, instantly different ship silhouettes with cross-hatching for shade;
- flat paper cut-outs for ships, portraits, buttons, and resource symbols;
- minimal animation: a subtle two-frame line wobble is enough;
- large handwritten labels and uncluttered panels, with gameplay values still
  typeset clearly enough to read at a glance.

Do not use photorealistic key art, glossy metal panels, chrome borders, or dense
3D HUD decoration as the primary style. The older board-game paintings set the
cyan/orange palette and brush texture; notebook paper, imperfect ink, and clear
flat symbols keep that style readable during a fast RTS match.

Original art should be copied, never moved, into a clearly named `source_art/`
subfolder. Each imported file should be listed in the asset manifest with its
original path and author. Runtime-ready derivatives belong under the normal
`images/`, `materials/`, or model folders.

## Alpha definition of done

- A fresh player can start and finish a Human-versus-Rebel match without
  encountering vanilla diplomacy, Influence, population, native resources,
  ship design, or alternate victory systems.
- Both factions can build ships, research all four upgrades, Conquer neutral
  territory, Bombard defenses, and win.
- The default match is symmetric, is playable in 15-30 minutes, and cannot run
  beyond the 30-minute tiebreak.
- Automated data tests protect the map size, time limit, feature cuts, build
  pacing, roster, and research scope; an engine smoke test compiles every
  AngelScript context.

## Known implementation boundary

The computer player still expands through Star Ruler 2's internal colonization
logic. That path remains temporarily because removing it before the AI can use
the Conquer ability would leave the opponent unable to expand. It is an
explicit technical bridge, not a player-facing rule.

The game was previously called **Torcan**. The older board-game archive was found at
`C:\Users\Tolga\Desktop\Assets, backgrounds`. Its hand-painted cyan/orange
background, planet, station, card, and symbol art now defines the visual
reference language alongside the notebook-paper UI. The archive does not
contain a separate named ship roster, so station paintings are kept semantic
and are not misrepresented as ships. Ship-model integration remains a distinct
follow-up when original 3D meshes are located. The Torcan Drive archive now
supplies the canonical 2D fleet silhouettes for design, build, queue, popup,
and selected-ship UI.
