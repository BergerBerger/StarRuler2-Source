import elements.BaseGuiElement;
import elements.GuiButton;
import elements.GuiContextMenu;
import elements.MarkupTooltip;
import buildings;
import icons;

export SlotGridPanel;

const int SLOT_SIZE = 42;
const int SLOT_GAP = 6;

//Only our own building types -- the base game ships with dozens of other
//building types (vanilla economy, defense, ancient ruins, etc.) that were
//never removed from the registry, just left mostly un-buildable. Iterating
//the whole registry let a few of those leak into the build menu; whitelist
//ours explicitly instead.
const array<string> OUR_BUILDING_IDENTS = {"MiningUnit", "EnergyHarvesterUnit", "SpaceportUnit", "ResearchComplex", "StarHarvester"};

//A plain (non-modal) row of square buttons, one per buildable slot on the
//object -- no dimmed background, no exclusive focus, no separate menu.
//Click an empty square to pick what to build there; click a built one to
//destroy it. Positioned beside the InfoBar so it reads as part of the same
//selection panel instead of a popup.
//
//Slots fill/empty in the same fixed sequential order buildBuilding()/
//destroyBuilding() already use elsewhere (no real click-a-tile positioning).
class SlotGridPanel : BaseGuiElement {
	Object@ obj;
	array<GuiButton@> squares;
	GuiButton@ shipButton;

	SlotGridPanel(IGuiElement@ parent, Object@ Obj) {
		@obj = Obj;
		super(parent, Alignment(Left+470, Bottom-228, Left+470+560, Bottom-228+SLOT_SIZE));
		rebuild();
		updateAbsolutePosition();
	}

	bool compatible(Object@ o) {
		return o is obj;
	}

	void rebuild() {
		for(uint i = 0, cnt = squares.length; i < cnt; ++i)
			squares[i].remove();
		squares.length = 0;
		if(shipButton !is null) {
			shipButton.remove();
			@shipButton = null;
		}

		if(obj is null || !obj.hasSurfaceComponent)
			return;

		int total = obj.surfaceGridSize.x;
		int built = int(obj.getBuildingCount());
		for(int i = 0; i < total; ++i) {
			bool filled = i < built;
			Sprite spr = icons::Plus;
			string tt = locale::TT_BUILD_SLOT;
			if(filled) {
				uint typeId = obj.buildingType[uint(i)];
				const BuildingType@ type = getBuildingType(typeId);
				spr = type !is null ? type.sprite : icons::Building;
				tt = type !is null ? type.name : locale::TT_DESTROY_SLOT;
			}
			GuiButton@ btn = GuiButton(this, recti_area(i*(SLOT_SIZE+SLOT_GAP), 0, SLOT_SIZE, SLOT_SIZE), spr);
			btn.style = SS_IconButton;
			setMarkupTooltip(btn, tt, width=300);
			squares.insertLast(btn);
		}

		//A built Spaceport unlocks ship construction on this body; show a
		//separate button for it (ships don't occupy a slot square -- they
		//go into their own construction queue, same as vanilla).
		if(obj.hasConstruction && obj.canBuildShips) {
			int x = total*(SLOT_SIZE+SLOT_GAP) + SLOT_GAP;
			@shipButton = GuiButton(this, recti_area(x, 0, SLOT_SIZE, SLOT_SIZE), icons::Ship);
			shipButton.style = SS_IconButton;
			setMarkupTooltip(shipButton, locale::TT_BUILD_SHIP, width=300);
		}
	}

	double updateTimer = 0.0;
	void update(double time) {
		updateTimer -= time;
		if(updateTimer <= 0) {
			updateTimer = 0.3;
			rebuild();
		}
	}

	bool onGuiEvent(const GuiEvent& evt) override {
		if(evt.type == GUI_Clicked) {
			if(evt.caller is shipButton) {
				openShipMenu();
				return true;
			}
			int idx = squares.find(cast<GuiButton>(evt.caller));
			if(idx != -1) {
				if(idx < int(obj.getBuildingCount()))
					openDestroyMenu(idx);
				else
					openBuildMenu();
				return true;
			}
		}
		return BaseGuiElement::onGuiEvent(evt);
	}

	void openShipMenu() {
		if(obj.owner !is playerEmpire || !obj.hasConstruction || !obj.canBuildShips)
			return;
		GuiContextMenu menu(mousePos);
		ReadLock lock(playerEmpire.designMutex);
		uint clsCount = playerEmpire.designClassCount;
		for(uint i = 0; i < clsCount; ++i) {
			const DesignClass@ cls = playerEmpire.getDesignClass(i);
			for(uint j = 0, jcnt = cls.designCount; j < jcnt; ++j) {
				const Design@ dsg = cls.designs[j];
				if(dsg.obsolete)
					continue;
				if(dsg.hasTag(ST_Station) || dsg.hasTag(ST_Satellite) || dsg.hasTag(ST_Support))
					continue;
				menu.addOption(BuildShipOption(obj, dsg));
			}
		}
		menu.finalize();
	}

	void openBuildMenu() {
		if(obj.owner !is playerEmpire)
			return;
		GuiContextMenu menu(mousePos);
		for(uint i = 0, cnt = getBuildingTypeCount(); i < cnt; ++i) {
			const BuildingType@ type = getBuildingType(i);
			if(OUR_BUILDING_IDENTS.find(type.ident) == -1)
				continue;
			if(!type.canBuildOn(obj, ignoreState=true))
				continue;
			//Star Harvester is a sun-only building; everything else can't
			//be built on a sun.
			bool isStarHarvester = type.ident == "StarHarvester";
			if(obj.isStar != isStarHarvester)
				continue;
			menu.addOption(BuildSlotOption(obj, type));
		}
		menu.finalize();
	}

	void openDestroyMenu(int idx) {
		if(obj.owner !is playerEmpire)
			return;
		GuiContextMenu menu(mousePos);
		menu.addOption(DestroySlotOption(obj, idx));
		menu.finalize();
	}
};

class BuildSlotOption : GuiContextOption {
	Object@ obj;
	const BuildingType@ type;

	BuildSlotOption(Object@ o, const BuildingType@ t) {
		@obj = o;
		@type = t;
		text = type.name;
		icon = type.sprite;
	}

	void call(GuiContextMenu@ menu) override {
		//Always append after whatever's already built, same slot the
		//existing ConstructionOverlay build flow uses.
		obj.buildBuilding(type.id, vec2i(obj.getBuildingCount(), 0));
	}
};

class BuildShipOption : GuiContextOption {
	Object@ obj;
	const Design@ dsg;

	BuildShipOption(Object@ o, const Design@ d) {
		@obj = o;
		@dsg = d;
		text = dsg.name;
		icon = dsg.icon;
	}

	void call(GuiContextMenu@ menu) override {
		obj.buildFlagship(dsg);
	}
};

class DestroySlotOption : GuiContextOption {
	Object@ obj;
	int idx;

	DestroySlotOption(Object@ o, int i) {
		@obj = o;
		idx = i;
		text = locale::DESTROY_BUILDING_GENERIC;
	}

	void call(GuiContextMenu@ menu) override {
		obj.destroyBuilding(vec2i(idx, 0));
	}
};
