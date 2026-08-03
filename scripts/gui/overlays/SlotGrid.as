import elements.BaseGuiElement;
import elements.GuiButton;
import elements.GuiContextMenu;
import elements.MarkupTooltip;
import buildings;
import icons;

export SlotGridPanel;

const int SLOT_SIZE = 42;
const int SLOT_GAP = 6;

//A plain (non-modal) row of square buttons, one per buildable slot on the
//object -- no dimmed background, no exclusive focus, no separate menu.
//Click an empty square to pick what to build there; click a built one to
//destroy it. Positioned beside the InfoBar so it reads as part of the same
//selection panel instead of a popup.
//
//Per-slot building lookups (what's built at a given position) aren't part
//of the GUI-side object interface, only totals are (getBuildingCount(),
//surfaceGridSize) -- so filled squares show a generic built icon rather
//than each building's own icon, and slots fill/empty in the same fixed
//order buildBuilding()/destroyBuilding() already use elsewhere.
class SlotGridPanel : BaseGuiElement {
	Object@ obj;
	array<GuiButton@> squares;

	SlotGridPanel(IGuiElement@ parent, Object@ Obj) {
		@obj = Obj;
		super(parent, Alignment(Left+470, Bottom-228, Left+470+520, Bottom-228+SLOT_SIZE));
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

		if(obj is null || !obj.hasSurfaceComponent)
			return;

		int total = obj.surfaceGridSize.x;
		int built = int(obj.getBuildingCount());
		for(int i = 0; i < total; ++i) {
			bool filled = i < built;
			GuiButton@ btn = GuiButton(this, recti_area(i*(SLOT_SIZE+SLOT_GAP), 0, SLOT_SIZE, SLOT_SIZE),
					filled ? icons::Building : icons::Plus);
			btn.style = SS_IconButton;
			setMarkupTooltip(btn, filled ? locale::TT_DESTROY_SLOT : locale::TT_BUILD_SLOT, width=300);
			squares.insertLast(btn);
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

	void openBuildMenu() {
		if(obj.owner !is playerEmpire)
			return;
		GuiContextMenu menu(mousePos);
		for(uint i = 0, cnt = getBuildingTypeCount(); i < cnt; ++i) {
			const BuildingType@ type = getBuildingType(i);
			if(type.civilian)
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
