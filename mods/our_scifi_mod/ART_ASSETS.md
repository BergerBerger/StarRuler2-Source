# Art asset manifest

## Runtime assets

| Asset | Origin | Status | Purpose |
| --- | --- | --- | --- |
| `data/images/notebook_paper.png` | Generated for this repository with OpenAI image generation on 2026-08-09 | Replaceable alpha asset | Warm graph-paper surface behind the compact build-slot panel |
| `data/images/boardgame/menu_background.png` | Project board-game original, copied from `C:\Users\Tolga\Desktop\Assets, backgrounds\Sky Background No ships.png` | Imported runtime copy | Main-menu background for this mod |
| `data/images/boardgame/planet_eden.png` | Project board-game original, copied from `C:\Users\Tolga\Desktop\Assets, backgrounds\Planet 1.png` | Imported runtime copy | Planet UI art |
| `data/images/boardgame/alien_station.png` | Project board-game original, copied from `IMG_3323.PNG`; the Unity package names it `Alien Station.PNG` | Imported reference material | Station/capital-art reference; never used as a ship substitute |
| `data/images/boardgame/icarus_station.png` | Project board-game original, copied from `IMG_3319.PNG`; the Unity package names it `Icarus Station.PNG` | Imported reference material | Station/capital-art reference; never used as a ship substitute |
| `data/images/boardgame/icon_minerals.png` | OpenAI image edit based on `Mineral Icon 2.png` and `Building Card Example.png` | Runtime alpha asset | Minerals UI and map-resource icon |
| `data/images/boardgame/icon_energy.png` | OpenAI image edit based on `Energy Icon 2.png` and `Building Card Example.png` | Runtime alpha asset | Energy UI and map-resource icon |
| `data/images/boardgame/icon_research.png` | OpenAI image edit based on `Science Icon 2.png` and `Science Card Example.png` | Runtime alpha asset | Research UI icon |
| `data/images/boardgame/icon_station.png` | OpenAI image edit based on `Space Station Icon.png` and `Station Background.png` | Runtime alpha asset | Orbital/station UI icon |

The four regenerated icons were produced in image-edit mode on 2026-08-09.
Each prompt preserved the original symbol while requesting an imperfect navy-ink
outline, the board game's cyan/orange paint palette, real brush texture, a
simple 24-pixel-readable silhouette, and a solid magenta chroma background.
The checked-in runtime PNGs were converted to transparent alpha with the
ImageGen skill's chroma-key removal script. Disposable chroma intermediates are
not checked in; the source references and edit recipe above are the provenance
record.

## Preserved board-game originals

The files in `source_art/boardgame_originals/` are byte-for-byte copies from
`C:\Users\Tolga\Desktop\Assets, backgrounds`. They were copied rather than
moved so the old board-game folder remains intact.

| Preserved file | Original filename | Role |
| --- | --- | --- |
| `alien_station.png` | `IMG_3323.PNG` | Alien station painting |
| `icarus_station.png` | `IMG_3319.PNG` | Icarus station painting |
| `sky_fleet.png` | `Sky Background.png` | Painted background with two small ships; fleet style reference only |
| `sky_background_no_ships.png` | `Sky Background No ships.png` | Clean painted background |
| `planet_eden.png` | `Planet 1.png` | Painted planet |
| `icon_minerals.png` | `Mineral Icon 2.png` | Original minerals symbol |
| `icon_energy.png` | `Energy Icon 2.png` | Original energy symbol |
| `icon_research.png` | `Science Icon 2.png` | Original research symbol |
| `icon_station.png` | `Space Station Icon.png` | Original station symbol |
| `reference_building_card.png` | `Building Card Example.png` | Card palette and typography reference |
| `reference_action_card.png` | `Action Card Example.png` | Card palette and typography reference |
| `reference_science_card.png` | `Science Card Example.png` | Card palette and typography reference |
| `reference_planet_card.png` | `Planet Card Example.png` | Card layout reference |

## Other located material

- `C:\Users\Tolga\OneDrive\planeten-spiel` contains Unreal `.uasset` ship and
  planet assets from a later version of the project.
- `C:\Users\Tolga\Documents\Codex\2026-07-30\prior-conversation-with-codex-conversation-role-2\work\planeten-spiel\SourceArt`
  contains polished/photoreal space art and portrait atlases.

Those locations are not part of this board-game import. The board-game archive
does not contain a separate, named ship roster: its two large spacecraft
paintings are explicitly station art, and `Sky Background.png` contains only
two small ships baked into a background. The future ship-model import remains
intentionally open.

Future original scans or ship models should be copied, never moved, into a
clearly named `source_art/` subfolder. Add original path and author here before
creating runtime derivatives under the normal mod `images/`, `materials/`, or
model folders.

## Torcan ship archive

The project's earlier name was **Torcan**. The historical fleet archive was
found in Google Drive folder
`17BAXBkGdEeMIvJY6ATGfu-0VRNzkyY6G`. Its `manifest.csv` traces the ship files
to `D:\Game Projects\TCG Project\Assets\Planet Game Assets` and the detailed
concept to `D:\Desktop Ordner\Boardgame\spaceship drawing 1.psd`.

Drive's ten authenticated raw PNG downloads are preserved byte-for-byte under
`source_art/torcan_drive_originals/`. Runtime derivatives under
`data/images/ships/torcan/` trim transparent margins, center each silhouette on
a padded square canvas, and preserve the source pixels. The PSD is represented
only by an authenticated preview render.

| Runtime file | Drive source | Current role |
| --- | --- | --- |
| `small_ship_lvl1.png` | `Objects/S-Ship lvl 1.png` | Human small warship |
| `medium_ship_lvl1.png` | `Objects/M-Ships lvl 1.png` | Human medium warship |
| `large_ship_lvl1.png` | `Objects/L-Ship lvl 1.png` | Human large warship |
| `engineering_drone.png` | `Objects/Engineering drone.png` | Human scout |
| `destroyer_alpha.png` | `Objects/DestroyerAlpha.png` | Human capital ship |
| `small_ship_lvl2.png` | `Objects/S-Ship lvl 2.png` | Rebel small warship |
| `medium_ship_lvl2.png` | `Objects/M-Ship lvl 2.png` | Rebel medium warship |
| `large_ship_lvl2.png` | `L-Ship lvl 2.png` | Rebel large warship |
| `destroyer_ship_lvl2.png` | `Destroyer ship 2.png` | Rebel capitol ship |
| `colony_ship.png` | `Objects/Colony ship 1.png` | Preserved future utility role |

`spaceship_drawing_preview.png` is a preview render of the detailed orange
`spaceship drawing 1.psd` and remains reference-only. These files are 2D ship
art, not 3D meshes: the alpha uses them consistently in build/queue/selection
UI while retaining its current world-space geometry.
