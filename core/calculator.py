import math

from .constants import FIELD_YIELD, ANIMALS_PER_PLOT, ANIMAL_YIELD
from .data_loader import RECIPES, FEED_MAP


def resolve_ingredient(source, qty, crop_demand, animal_demand):

    # Animal source
    if source in ANIMAL_YIELD:
        animal_demand[source] = animal_demand.get(source, 0) + qty
        return

    # Craftable ingredient
    if source in RECIPES:

        recipe = RECIPES[source]

        for ing, data in recipe["ingredients"].items():

            resolve_ingredient(
                data["source"],
                data["qty"] * qty,
                crop_demand,
                animal_demand
            )

    # Base crop
    else:
        crop_demand[source] = crop_demand.get(source, 0) + qty


def calculate_layout(recipe_key, island_plots):

    recipe = RECIPES[recipe_key]

    crop_demand = {}
    animal_demand = {}

    # Resolve all ingredients
    for ing, data in recipe["ingredients"].items():

        resolve_ingredient(
            data["source"],
            data["qty"],
            crop_demand,
            animal_demand
        )

    pasture_plots = {}

    # Convert animals to plots
    for animal, qty in animal_demand.items():

        yield_per_animal = ANIMAL_YIELD[animal]["yield"]

        animals_needed = qty / yield_per_animal

        plots = animals_needed / ANIMALS_PER_PLOT

        pasture_plots[animal] = plots

        # Add feed demand
        if animal in FEED_MAP:

            feed = FEED_MAP[animal]["feed"]
            feed_qty = animals_needed * FEED_MAP[animal]["feed_qty"]

            crop_demand[feed] = crop_demand.get(feed, 0) + feed_qty

    field_plots = {}

    # Convert crops to fields
    for crop, qty in crop_demand.items():

        field_plots[crop] = qty / FIELD_YIELD

    # Scaling to island size
    total_plots = sum(pasture_plots.values()) + sum(field_plots.values())

    scale = island_plots / total_plots if total_plots > 0 else 1

    for k in pasture_plots:
        pasture_plots[k] = math.ceil(pasture_plots[k] * scale)

    for k in field_plots:
        field_plots[k] = math.ceil(field_plots[k] * scale)

    total = sum(pasture_plots.values()) + sum(field_plots.values())

    # Reduce overflow
    while total > island_plots:

        largest = max(field_plots, key=field_plots.get)

        if field_plots[largest] > 1:
            field_plots[largest] -= 1
            total -= 1
        else:
            break

    return pasture_plots, field_plots