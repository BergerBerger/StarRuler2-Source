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


if __name__ == "__main__":
    unittest.main()
