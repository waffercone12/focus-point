import discord
from discord import app_commands
import json
import os
import math
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# =============================
# GAME CONSTANTS
# =============================

FIELD_YIELD = 90
ANIMALS_PER_PLOT = 9

ANIMAL_YIELD = {
    "Pig": {"product": "Raw Pork", "yield": 21},
    "Goose": {"product": "Goose Egg", "yield": 5},
    "Chicken": {"product": "Chicken Egg", "yield": 5},
    "Cow": {"product": "Raw Beef", "yield": 21},
    "Sheep": {"product": "Raw Mutton", "yield": 21},
    "Goat": {"product": "Raw Goat", "yield": 21}
}

# =============================
# LOAD DATA
# =============================

with open("recipes.json") as f:
    RECIPES = json.load(f)

with open("feed_map.json") as f:
    FEED_MAP = json.load(f)

# =============================
# CALCULATION ENGINE
# =============================

def calculate_layout(recipe_key, island_plots):

    recipe = RECIPES[recipe_key]

    crop_demand = {}
    animal_demand = {}

    # -------------------------
    # Parse recipe ingredients
    # -------------------------

    for ing, data in recipe["ingredients"].items():

        source = data["source"]
        qty = data["qty"]

        if source in ANIMAL_YIELD:
            animal_demand[source] = animal_demand.get(source, 0) + qty
        else:
            crop_demand[source] = crop_demand.get(source, 0) + qty

    pasture_plots = {}

    # -------------------------
    # Convert animal products
    # -------------------------

    for animal, qty in animal_demand.items():

        yield_per_animal = ANIMAL_YIELD[animal]["yield"]

        animals_needed = qty / yield_per_animal

        plots = animals_needed / ANIMALS_PER_PLOT

        pasture_plots[animal] = plots

        # Feed calculation
        if animal in FEED_MAP:

            feed = FEED_MAP[animal]["feed"]
            feed_qty = animals_needed * FEED_MAP[animal]["feed_qty"]

            crop_demand[feed] = crop_demand.get(feed, 0) + feed_qty

    field_plots = {}

    # -------------------------
    # Convert crops to fields
    # -------------------------

    for crop, qty in crop_demand.items():

        field_plots[crop] = qty / FIELD_YIELD

    # -------------------------
    # Scale to island size
    # -------------------------

    total_plots = sum(pasture_plots.values()) + sum(field_plots.values())

    scale = island_plots / total_plots

    for k in pasture_plots:
        pasture_plots[k] = math.ceil(pasture_plots[k] * scale)

    for k in field_plots:
        field_plots[k] = math.ceil(field_plots[k] * scale)

    # -------------------------
    # Adjust if plots exceed island size
    # -------------------------

    total = sum(pasture_plots.values()) + sum(field_plots.values())

    while total > island_plots:

        # reduce largest field first
        largest = max(field_plots, key=field_plots.get)

        if field_plots[largest] > 1:
            field_plots[largest] -= 1
            total -= 1
        else:
            break

    return pasture_plots, field_plots

# =============================
# DISCORD BOT
# =============================

class AlbionBot(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = AlbionBot()

# =============================
# COMMAND OPTIONS
# =============================

recipe_choices = [
    app_commands.Choice(name=k, value=k)
    for k in RECIPES.keys()
][:25]

# =============================
# OPTIMIZE COMMAND
# =============================

@bot.tree.command(name="optimize", description="Sustainable island farm layout")
@app_commands.choices(recipe=recipe_choices)
@app_commands.describe(
    recipe="Select recipe",
    plots="Total island plots"
)
async def optimize(interaction: discord.Interaction, recipe: app_commands.Choice[str], plots: int):

    pasture, fields = calculate_layout(recipe.value, plots)

    embed = discord.Embed(
        title=f"Island Layout — {recipe.value}",
        color=0x9b59b6
    )

    pasture_text = ""

    for animal, p in pasture.items():
        pasture_text += f"{animal}: {p} plots\n"

    field_text = ""

    for crop, p in fields.items():
        field_text += f"{crop}: {p} plots\n"

    embed.add_field(name="Pasture Plots", value=pasture_text or "None", inline=False)
    embed.add_field(name="Field Plots", value=field_text or "None", inline=False)

    await interaction.response.send_message(embed=embed)

# =============================
# RUN BOT
# =============================

bot.run(TOKEN)