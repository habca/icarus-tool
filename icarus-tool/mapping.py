def recipe_sets_to_outputs(row_name: str) -> str:
    if row_name in workstations:
        return workstations[row_name]
    return row_name


# TODO: miksei testit paljastanut mortar_and_pestle?
workstations = {
    "machining_bench": "kit_machining_bench",
    "mortar_and_pestle": "kit_mortar_and_pestle",
    "rustic_decorations_bench": "rustic_decoration_bench",
}


def outputs_to_tech_tree(row_name: str) -> str:
    raise NotImplementedError


crafting_items = {
    "aluminium": "aluminium_ingot",
    "bauxite": "aluminium_ore",
    "metal_ore": "iron_ore",
    "refined_copper": "copper_ingot",
    "refined_metal": "iron_ingot",
}
