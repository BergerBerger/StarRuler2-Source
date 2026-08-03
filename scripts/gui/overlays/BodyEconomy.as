#include "include/resource_constants.as"

import tile_resources;
import util.formatting;

double getBodyMineralsPerCycle(Object@ obj) {
	if(obj is null || !obj.hasSurfaceComponent)
		return 0.0;
	return max(obj.getResourceProduction(TR_Money), 0.0);
}

double getBodyEnergyPerCycle(Object@ obj) {
	if(obj is null || !obj.hasSurfaceComponent)
		return 0.0;
	return max(obj.getResourceProduction(TR_Energy), 0.0) * ENERGY_RESOURCE_PER_CYCLE;
}

string formatBodyProduction(Object@ obj, bool explain = false) {
	string text = "[font=Medium][b]"+locale::BODY_PRODUCTION_CYCLE+"[/b][/font]\n";
	text += format("[img=$1;22/] $2: [b]+$3[/b]\n",
		getTileResourceSpriteSpec(TR_Money), locale::RESOURCE_MONEY,
		standardize(getBodyMineralsPerCycle(obj), true));
	text += format("[img=$1;22/] $2: [b]+$3[/b]",
		getTileResourceSpriteSpec(TR_Energy), locale::RESOURCE_ENERGY,
		standardize(getBodyEnergyPerCycle(obj), true));
	if(explain)
		text += "\n[color=#aaa]"+locale::BODY_PRODUCTION_CYCLE_TIP+"[/color]";
	return text;
}

string formatBodyProductionCompact(Object@ obj) {
	string text = format("[img=$1;16/] +$2 $3\n",
		getTileResourceSpriteSpec(TR_Money),
		standardize(getBodyMineralsPerCycle(obj), true), locale::RESOURCE_MONEY);
	text += format("[img=$1;16/] +$2 $3",
		getTileResourceSpriteSpec(TR_Energy),
		standardize(getBodyEnergyPerCycle(obj), true), locale::RESOURCE_ENERGY);
	return text;
}
