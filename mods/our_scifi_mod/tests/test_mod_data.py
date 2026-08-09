import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "mods" / "our_scifi_mod"


def resolved_overlay(relative_dir: str) -> dict[str, Path]:
    """Return effective base+mod data files after path-based overrides."""
    files: dict[str, Path] = {}
    for data_root in (ROOT / "data", MOD / "data"):
        directory = data_root / relative_dir
        if not directory.exists():
            continue
        for path in directory.rglob("*.txt"):
            files[path.relative_to(directory).as_posix()] = path
    return files


def definitions(relative_dir: str, kind: str) -> set[str]:
    pattern = re.compile(
        rf"^\s*{re.escape(kind)}:\s*([A-Za-z_][A-Za-z0-9_]*)",
        re.MULTILINE,
    )
    found: set[str] = set()
    for path in resolved_overlay(relative_dir).values():
        found.update(pattern.findall(path.read_text(encoding="utf-8-sig")))
    return found


def design_names(directory: str) -> set[str]:
    names: set[str] = set()
    for path in (MOD / "data" / "designs" / directory).glob("*.design"):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        name = data["name"]
        if name in names:
            raise AssertionError(f"Duplicate design name {name!r} in {directory}")
        names.add(name)
    return names


class ModDataTests(unittest.TestCase):
    def test_active_abilities_only_reference_defined_planetary_resources(self) -> None:
        resources = definitions("resources", "Resource")
        reference = re.compile(r"AddPlanetResource\(\s*([A-Za-z_][A-Za-z0-9_]*)")
        missing: list[str] = []

        for relative, path in resolved_overlay("abilities").items():
            for resource in reference.findall(path.read_text(encoding="utf-8-sig")):
                if resource not in resources:
                    missing.append(f"{relative}: {resource}")

        self.assertEqual(
            [],
            missing,
            "Dangling AddPlanetResource hooks: " + ", ".join(missing),
        )

    def test_active_artifacts_only_reference_defined_abilities(self) -> None:
        abilities = definitions("abilities", "Ability")
        reference = re.compile(
            r"^\s*Ability:\s*([A-Za-z_][A-Za-z0-9_]*)",
            re.MULTILINE,
        )
        missing: list[str] = []

        for relative, path in resolved_overlay("artifacts").items():
            for ability in reference.findall(path.read_text(encoding="utf-8-sig")):
                if ability not in abilities:
                    missing.append(f"{relative}: {ability}")

        self.assertEqual(
            [],
            missing,
            "Artifacts reference missing abilities: " + ", ".join(missing),
        )

    def test_enslave_is_disabled_with_the_removed_slave_labor_resource(self) -> None:
        enslave = resolved_overlay("abilities")["common/Enslave.txt"]
        content = enslave.read_text(encoding="utf-8-sig")
        self.assertNotIn("Ability: Enslave", content)
        self.assertNotIn("AddPlanetResource", content)
        self.assertNotIn("SlaveLabor", definitions("resources", "Resource"))

        mind_control = resolved_overlay("artifacts")["_old/MindControl.txt"]
        self.assertNotIn(
            "Artifact: MindControl",
            mind_control.read_text(encoding="utf-8-sig"),
        )

    def test_fixed_design_rosters_are_faction_scoped(self) -> None:
        self.assertEqual(
            {"Small Warship", "Medium Warship", "Large Warship"},
            design_names("our_presets"),
        )
        self.assertEqual(
            {"Scout", "Capital Ship"},
            design_names("our_human_presets"),
        )
        self.assertEqual({"Capitol"}, design_names("our_rebel_presets"))

    def test_faction_traits_load_their_expected_rosters(self) -> None:
        human = (MOD / "data/traits/government/HumanGovernment.txt").read_text(
            encoding="utf-8-sig"
        )
        rebel = (MOD / "data/traits/government/RebelGovernment.txt").read_text(
            encoding="utf-8-sig"
        )
        capitol = (MOD / "data/traits/lifestyle/RebelCapitol.txt").read_text(
            encoding="utf-8-sig"
        )

        self.assertIn("LoadDesigns(our_presets, False, False)", human)
        self.assertIn("LoadDesigns(our_human_presets, False, False)", human)
        self.assertIn("LoadDesigns(our_presets, False, False)", rebel)
        self.assertIn("LoadDesigns(our_rebel_presets, False, False)", capitol)
        self.assertLess(
            capitol.index("UnlockSubsystem(MothershipHull)"),
            capitol.index("LoadDesigns(our_rebel_presets"),
        )

    def test_fixed_rosters_are_not_injected_into_every_empire(self) -> None:
        empire_script = (ROOT / "scripts/server/empire.as").read_text(
            encoding="utf-8-sig"
        )
        self.assertNotIn("ourPresetDesigns", empire_script)
        self.assertNotIn('readDirectory("data/designs/our_presets")', empire_script)

    def test_default_match_is_humans_versus_rebels(self) -> None:
        settings = (ROOT / "scripts/shared/settings/game_settings.as").read_text(
            encoding="utf-8-sig"
        )
        defaults = settings.split("void defaults()", 1)[1].split("void setNamed", 1)[0]
        self.assertIn("empires.length = 2;", defaults)
        for required in (
            'empires[0].raceName = "Humans";',
            'empires[1].raceName = "Rebels";',
            'empires[0].chooseTrait(getTrait("HumanGovernment"));',
            'empires[1].chooseTrait(getTrait("RebelGovernment"));',
            'empires[1].chooseTrait(getTrait("RebelCapitol"));',
        ):
            self.assertIn(required, defaults)

    def test_headless_script_mode_does_not_initialize_graphics(self) -> None:
        initialization = (ROOT / "source/game/main/initialization.cpp").read_text(
            encoding="utf-8-sig"
        )
        function = initialization.split(
            "bool initGlobal(bool loadGraphics, bool createWindow)", 1
        )[1].split("void cleanupGlobal()", 1)[0]

        self.assertLess(
            function.index("load_resources = loadGraphics;"),
            function.index("if(loadGraphics)"),
        )
        self.assertIn("getGLFWDriver(createWindow)", function)
        self.assertNotIn("getGLFWDriver()", function)

        glfw_driver = (ROOT / "source/game/os/glfw_driver.cpp").read_text(
            encoding="utf-8-sig"
        )
        key_lookup = glfw_driver.split(
            "int getKeyForChar(unsigned char chr)", 1
        )[1].split("unsigned getDoubleClickTime()", 1)[0]
        self.assertIn("if(!glfwInitialized)", key_lookup)
        self.assertIn("return chr;", key_lookup)

    def test_energy_buildings_use_normalized_rts_rates(self) -> None:
        energy_sources = {
            "EnergyHarvesterUnit.txt": 2.0,
            "StarHarvester.txt": 20.0,
        }
        buildings = MOD / "data/buildings/our_buildings"
        add_energy = re.compile(r"AddResource\(Energy,\s*([0-9.]+)\)")

        for filename, expected_per_cycle in energy_sources.items():
            content = (buildings / filename).read_text(encoding="utf-8-sig")
            match = add_energy.search(content)
            self.assertIsNotNone(match, f"{filename} has no Energy production")
            tile_rate = float(match.group(1))
            self.assertAlmostEqual(
                expected_per_cycle,
                tile_rate * 0.5 * 60.0,
                places=6,
                msg=f"{filename} does not match its 60-second RTS output",
            )

    def test_body_energy_baselines_are_continuous_and_visible_to_ui(self) -> None:
        sources = {
            "Planet.as": ("energyTurnTimer", "modEnergyStored(baseEnergy)"),
            "Star.as": ("turnTimer", "modEnergyStored(baseEnergy)"),
            "Orbital.as": ("turnTimer", "modEnergyStored(2.0)"),
            "Ship.as": ("turnTimer", "modEnergyStored(3.0)"),
        }
        objects = ROOT / "scripts/server/objects"
        for filename, removed_patterns in sources.items():
            content = (objects / filename).read_text(encoding="utf-8-sig")
            self.assertIn("ENERGY_RESOURCE_PER_CYCLE", content)
            for pattern in removed_patterns:
                self.assertNotIn(pattern, content)

        helper = (ROOT / "scripts/gui/overlays/BodyEconomy.as").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("getResourceProduction(TR_Money)", helper)
        self.assertIn("getResourceProduction(TR_Energy)", helper)
        self.assertIn("ENERGY_RESOURCE_PER_CYCLE", helper)
        for filename in (
            "PlanetInfoBar.as",
            "AsteroidInfoBar.as",
            "StarInfoBar.as",
            "OrbitalInfoBar.as",
            "ShipInfoBar.as",
        ):
            content = (ROOT / "scripts/gui/overlays" / filename).read_text(
                encoding="utf-8-sig"
            )
            self.assertIn("formatBodyProduction", content)

    def test_planet_overlay_keeps_construction_and_hides_vanilla_management(self) -> None:
        overlay = (ROOT / "scripts/gui/overlays/PlanetOverlay.as").read_text(
            encoding="utf-8-sig"
        )
        constructor = overlay.split(
            "PlanetOverlay(IGuiElement@ parent, Planet@ Obj)", 1
        )[1].split("IGuiElement@ elementFromPosition", 1)[0]
        variables = overlay.split("void updateVars()", 1)[1].split(
            "bool onGuiEvent", 1
        )[0]

        self.assertIn("ConstructionDisplay(this", constructor)
        self.assertIn("SurfaceDisplay(this", constructor)
        self.assertNotIn("ResourceDisplay(this", constructor)
        self.assertIn("getBodyMineralsPerCycle", variables)
        self.assertIn("getBodyEnergyPerCycle", variables)
        for vanilla_detail in (
            "PLANET_POPULATION_TIP",
            "PLANET_PRESSURE_TIP",
            "PLANET_LOYALTY_TIP",
            "PLANET_INFLUENCE_TIP",
        ):
            self.assertNotIn(vanilla_detail, variables)

    def test_starting_minerals_are_locked_to_fifty(self) -> None:
        constants = (ROOT / "scripts/shared/include/resource_constants.as").read_text(
            encoding="utf-8-sig"
        )
        empire = (ROOT / "scripts/server/empire.as").read_text(
            encoding="utf-8-sig"
        )

        self.assertRegex(constants, r"const int STARTING_MINERALS\s*=\s*50\s*;")
        init = empire.split("void init(Empire& emp)", 1)[1].split(
            "uint getMajorEmpireCount", 1
        )[0]
        self.assertEqual(
            1,
            init.count("modTotalBudget(+STARTING_MINERALS, MoT_Planet_Income)"),
        )
        self.assertNotRegex(init, r"modTotalBudget\(\+?500\b")

    def test_bombard_then_conquer_is_the_universal_capture_flow(self) -> None:
        conquer = (
            MOD / "data/abilities/our_abilities/ConquerPlanet.txt"
        ).read_text(encoding="utf-8-sig")
        bombard = (
            MOD / "data/abilities/our_abilities/BombardPlanet.txt"
        ).read_text(encoding="utf-8-sig")

        self.assertIn(
            "Either(TargetFilterSpace(targ), Both(TargetFilterOtherEmpire(targ), TargetFilterNoBuildings(targ)))",
            conquer,
        )
        self.assertRegex(
            conquer,
            r"AfterChannel\(targ,\s*8,\s*TakeControl\(\),\s*Clear\s*=\s*False\)",
        )
        self.assertNotRegex(conquer, r"AfterChannel\(targ,\s*60\b")
        for body_type in ("Planet", "Asteroid", "Star", "Orbital"):
            self.assertIn(f"TargetFilterType(targ, {body_type})", conquer)
            self.assertIn(f"TargetFilterType(targ, {body_type})", bombard)

        self.assertIn("TargetFilterOtherEmpire(targ)", bombard)
        self.assertIn("TargetFilterHasBuildings(targ)", bombard)
        self.assertRegex(
            bombard,
            r"AfterChannel\(targ,\s*3,\s*DestroyABuilding\(\),\s*Clear\s*=\s*False\)",
        )

    def test_player_ui_has_no_colonize_bypass(self) -> None:
        overlays = ROOT / "scripts/gui/overlays"
        context_menu = (overlays / "ContextMenu.as").read_text(
            encoding="utf-8-sig"
        )
        menu_builder = context_menu.split(
            "bool openContextMenu(Object& clicked, Object@ selected = null)", 1
        )[1]
        self.assertNotRegex(
            menu_builder,
            r"addOption\([^;]*(?:AutoColonize|Colonize|CancelColonize)",
        )

        player_surfaces = {
            "ContextMenu.as": context_menu,
            "PlanetInfoBar.as": (overlays / "PlanetInfoBar.as").read_text(
                encoding="utf-8-sig"
            ),
            "Quickbar.as": (overlays / "Quickbar.as").read_text(
                encoding="utf-8-sig"
            ),
            "commands.as": (ROOT / "scripts/client/commands.as").read_text(
                encoding="utf-8-sig"
            ),
        }
        for filename, content in player_surfaces.items():
            self.assertNotIn("playerEmpire.autoColonize", content, filename)
            self.assertNotRegex(content, r"\.colonize\(", filename)

        planet_info = player_surfaces["PlanetInfoBar.as"]
        self.assertNotIn("ColonizeAction", planet_info)
        self.assertNotIn("ColonizeThisAction", planet_info)

        quickbar = player_surfaces["Quickbar.as"]
        self.assertNotIn("ColonizingPlanets", quickbar)
        self.assertNotIn("ColonizeSafePlanets", quickbar)

        commands = player_surfaces["commands.as"]
        self.assertNotIn("doColonize", commands)
        self.assertNotIn("KB_COLONIZE", commands)

    def test_selecting_buildable_bodies_opens_their_slots(self) -> None:
        overlays = ROOT / "scripts/gui/overlays"
        for filename in (
            "PlanetInfoBar.as",
            "AsteroidInfoBar.as",
            "StarInfoBar.as",
            "OrbitalInfoBar.as",
        ):
            content = (overlays / filename).read_text(encoding="utf-8-sig")
            setter = content.split("void set(Object@ obj) override", 1)[1].split(
                "bool displays(Object@ obj) override", 1
            )[0]
            self.assertIn("showManage(obj);", setter, filename)

    def test_star_and_asteroid_slots_restore_the_compact_info_bar(self) -> None:
        overlays = ROOT / "scripts/gui/overlays"
        for filename in ("AsteroidInfoBar.as", "StarInfoBar.as"):
            content = (overlays / filename).read_text(encoding="utf-8-sig")
            update = content.split("void update(double time) override", 1)[1]
            for lifecycle_step in (
                "if(overlay !is null)",
                "if(overlay.parent is null)",
                "@overlay = null;",
                "visible = true;",
                "overlay.update(time);",
            ):
                self.assertIn(lifecycle_step, update, filename)

    def test_short_match_defaults_are_bounded_and_symmetric(self) -> None:
        settings = (ROOT / "scripts/shared/settings/game_settings.as").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('galaxies[0].map_id = "Dumbbell.DumbbellMap";', settings)
        self.assertIn("galaxies[0][0] = 10;", settings)
        self.assertIn("galaxies[0][2] = 1;", settings)
        self.assertIn("galaxies[0][3] = 1;", settings)

        config = (MOD / "data/game_config.txt").read_text(encoding="utf-8-sig")
        values = dict(
            re.findall(r"(?m)^([A-Z][A-Z0-9_]+):\s*([^\s/]+)", config)
        )
        self.assertEqual("30", values["GAME_TIME_LIMIT"])
        for disabled in (
            "PLANET_CONDITION_CHANCE",
            "ANOMALY_OCCURANCE",
            "REMNANT_OCCURANCE",
            "UNIQUE_SYSTEM_OCCURANCE",
            "UNIQUE_RESOURCE_OCCURANCE",
            "ARTIFACT_FREQUENCY",
            "ENABLE_CIVILIAN_TRADE",
            "ENABLE_UNIQUE_SPREADS",
            "ENABLE_REVENANT_PARTS",
            "ENABLE_DREAD_PIRATE",
            "RESOURCE_SCARCITY",
            "ENABLE_INFLUENCE_EVENTS",
            "PLANET_MOON_CHANCE",
            "ENABLE_TERRAFORMING",
            "PICK_SECRET_PROJECTS",
            "ENABLE_INFLUENCE_VICTORY",
        ):
            self.assertEqual("0", values[disabled], disabled)

    def test_alpha_exposes_only_five_fast_building_choices(self) -> None:
        slot_grid = (ROOT / "scripts/gui/overlays/SlotGrid.as").read_text(
            encoding="utf-8-sig"
        )
        whitelist = slot_grid.split("OUR_BUILDING_IDENTS = {", 1)[1].split(
            "};", 1
        )[0]
        self.assertEqual(
            {
                "MiningUnit",
                "EnergyHarvesterUnit",
                "SpaceportUnit",
                "ResearchComplex",
                "StarHarvester",
            },
            set(re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', whitelist)),
        )

        building_files = (
            MOD / "data/buildings/our_buildings/MiningUnit.txt",
            MOD / "data/buildings/our_buildings/EnergyHarvesterUnit.txt",
            MOD / "data/buildings/our_buildings/SpaceportUnit.txt",
            MOD / "data/buildings/our_buildings/StarHarvester.txt",
            MOD / "data/buildings/imperial/ResearchComplex.txt",
        )
        for path in building_files:
            content = path.read_text(encoding="utf-8-sig")
            self.assertRegex(content, r"(?m)^\s*Build Time:\s*30\s*$", path.name)

    def test_canonical_faction_research_has_four_short_projects(self) -> None:
        expected = {
            "HumanTech.txt": {
                "HumanExtraction",
                "HumanHull",
                "HumanRailguns",
                "HumanShields",
            },
            "RebelTech.txt": {
                "RebelWarpDrive",
                "RebelHull",
                "RebelPhaseJump",
                "RebelLasers",
            },
        }
        block_pattern = re.compile(
            r"^Technology:\s*(\w+)\s*$\n(.*?)(?=^Technology:|^Grid:|\Z)",
            re.MULTILINE | re.DOTALL,
        )

        for filename, expected_projects in expected.items():
            content = (MOD / "data/research" / filename).read_text(
                encoding="utf-8-sig"
            )
            blocks = dict(block_pattern.findall(content))
            projects = {name for name in blocks if not name.endswith("Root")}
            self.assertEqual(expected_projects, projects, filename)
            for project in projects:
                self.assertRegex(blocks[project], r"(?m)^\s*Point Cost:\s*30\s*$")
                self.assertRegex(blocks[project], r"(?m)^\s*Time Cost:\s*40\s*$")

    def test_research_abilities_and_extraction_hooks_are_live(self) -> None:
        abilities = definitions("abilities", "Ability")
        research = "\n".join(
            (MOD / "data/research" / filename).read_text(encoding="utf-8-sig")
            for filename in ("HumanTech.txt", "RebelTech.txt")
        )
        granted = set(re.findall(r"GrantFleetAbility\((\w+)\)", research))
        self.assertEqual(
            {"HumanEmergencyShields", "RebelWeaponOvercharge", "RebelPhaseJump"},
            granted,
        )
        self.assertTrue(granted <= abilities)

        buildings = MOD / "data/buildings/our_buildings"
        mining = (buildings / "MiningUnit.txt").read_text(encoding="utf-8-sig")
        energy = (buildings / "EnergyHarvesterUnit.txt").read_text(
            encoding="utf-8-sig"
        )
        star = (buildings / "StarHarvester.txt").read_text(encoding="utf-8-sig")
        self.assertIn(
            "AddResourceEmpireAttribute(Money, AdvancedExtraction, 1.0)", mining
        )
        for content in (energy, star):
            self.assertIn(
                "AddResourceEmpireAttribute(Energy, AdvancedExtraction, 0.0333333333)",
                content,
            )

        planet_effects = (ROOT / "scripts/definitions/planet_effects.as").read_text(
            encoding="utf-8-sig"
        )
        attribute_hook = planet_effects.split(
            "class AddResourceEmpireAttribute", 1
        )[1].split("class AddPressureEmpireAttribute", 1)[0]
        self.assertIn("if(obj.hasSurfaceComponent)", attribute_hook)
        self.assertNotIn("if(obj.isPlanet)", attribute_hook)

        ship = (ROOT / "scripts/server/objects/Ship.as").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('getUnlockTag("RebelPhaseJumpResearched")', ship)
        self.assertIn('getAbilityType("RebelPhaseJump")', ship)

    def test_boardgame_art_manifest_preserves_originals_and_runtime_assets(self) -> None:
        source = MOD / "source_art/boardgame_originals"
        runtime = MOD / "data/images/boardgame"
        preserved = {
            "alien_station.png",
            "icarus_station.png",
            "sky_fleet.png",
            "sky_background_no_ships.png",
            "planet_eden.png",
            "icon_minerals.png",
            "icon_energy.png",
            "icon_research.png",
            "icon_station.png",
            "reference_building_card.png",
            "reference_action_card.png",
            "reference_science_card.png",
            "reference_planet_card.png",
        }
        self.assertEqual(preserved, {path.name for path in source.glob("*.png")})

        expected_runtime = {
            "alien_station.png",
            "icarus_station.png",
            "menu_background.png",
            "planet_eden.png",
            "icon_minerals.png",
            "icon_energy.png",
            "icon_research.png",
            "icon_station.png",
        }
        self.assertEqual(expected_runtime, {path.name for path in runtime.glob("*.png")})

        manifest = (MOD / "ART_ASSETS.md").read_text(encoding="utf-8-sig")
        for name in preserved:
            self.assertIn(f"`{name}`", manifest)

    def test_boardgame_material_textures_exist_and_icons_have_alpha(self) -> None:
        materials = (MOD / "data/materials/boardgame_art.txt").read_text(
            encoding="utf-8-sig"
        )
        texture_paths = re.findall(r"(?m)^\s*Texture:\s*(.+?)\s*$", materials)
        self.assertEqual(17, len(texture_paths))
        for texture in texture_paths:
            self.assertTrue((ROOT / texture).is_file(), texture)

        # PNG IHDR color type 6 is RGBA. This protects the chroma-key cleanup.
        for name in (
            "icon_minerals.png",
            "icon_energy.png",
            "icon_research.png",
            "icon_station.png",
        ):
            header = (MOD / "data/images/boardgame" / name).read_bytes()[:26]
            self.assertEqual(b"\x89PNG\r\n\x1a\n", header[:8], name)
            self.assertEqual(6, header[25], f"{name} is not an RGBA PNG")

    def test_boardgame_style_is_wired_without_faking_ship_art(self) -> None:
        icons = (ROOT / "scripts/definitions/icons.as").read_text(
            encoding="utf-8-sig"
        )
        for material in (
            "BoardgameMineralsIcon",
            "BoardgameEnergyIcon",
            "BoardgameResearchIcon",
            "BoardgameStationIcon",
            "BoardgamePlanetArt",
        ):
            self.assertIn(f"material::{material}", icons)

        menu = (ROOT / "scripts/menu/menus.as").read_text(encoding="utf-8-sig")
        self.assertIn('topMod.ident == "our_scifi_mod"', menu)
        self.assertIn(
            'defaultBackground.load("mods/our_scifi_mod/data/images/boardgame/menu_background.png")',
            menu,
        )
        self.assertIn('defaultBackground.load("data/images/title_shot_BG.png")', menu)

        ship_surfaces = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in (
                ROOT / "scripts/gui/overlays/ShipInfoBar.as",
                *sorted((MOD / "data/designs").rglob("*.design")),
            )
        )
        self.assertNotIn("BoardgameAlienStationArt", ship_surfaces)
        self.assertNotIn("BoardgameIcarusStationArt", ship_surfaces)

    def test_torcan_drive_fleet_art_is_complete_and_role_mapped(self) -> None:
        runtime = MOD / "data/images/ships/torcan"
        expected = {
            "colony_ship.png",
            "destroyer_alpha.png",
            "destroyer_ship_lvl2.png",
            "engineering_drone.png",
            "large_ship_lvl1.png",
            "large_ship_lvl2.png",
            "medium_ship_lvl1.png",
            "medium_ship_lvl2.png",
            "small_ship_lvl1.png",
            "small_ship_lvl2.png",
        }
        self.assertEqual(expected, {path.name for path in runtime.glob("*.png")})
        for path in runtime.glob("*.png"):
            self.assertGreater(path.stat().st_size, 1000, path.name)

        source = MOD / "source_art/torcan_drive_originals"
        self.assertEqual(
            expected | {"spaceship_drawing_preview.png"},
            {path.name for path in source.glob("*.png")},
        )

        icons = (ROOT / "scripts/definitions/icons.as").read_text(
            encoding="utf-8-sig"
        )
        for faction, roles in {
            "human": (
                "TorcanSmallShip1",
                "TorcanMediumShip1",
                "TorcanLargeShip1",
                "TorcanEngineeringDrone",
                "TorcanDestroyerAlpha",
            ),
            "rebel": (
                "TorcanSmallShip2",
                "TorcanMediumShip2",
                "TorcanLargeShip2",
                "TorcanDestroyer2",
            ),
        }.items():
            for role in roles:
                self.assertIn(role, icons, f"missing {faction} art role {role}")
        self.assertIn("Sprite getShipArt(const Design@ dsg)", icons)

        for filename in (
            "Construction.as",
            "ShipInfoBar.as",
            "ShipPopup.as",
            "SlotGrid.as",
            "Supports.as",
        ):
            content = (ROOT / "scripts/gui/overlays" / filename).read_text(
                encoding="utf-8-sig"
            )
            self.assertIn("icons::getShipArt", content, filename)


if __name__ == "__main__":
    unittest.main()
