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


if __name__ == "__main__":
    unittest.main()
