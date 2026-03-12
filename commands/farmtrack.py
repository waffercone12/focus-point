import discord
from discord import app_commands

from core.calculator import calculate_layout
from core.data_loader import RECIPES
from utils.farm_tracker_view import FarmTrackerView


def register(tree):

    recipe_choices = [
        app_commands.Choice(name=k, value=k)
        for k in RECIPES.keys()
    ][:25]

    @tree.command(name="farmtrack", description="Track farming progress")
    @app_commands.choices(recipe=recipe_choices)
    async def farmtrack(
        interaction: discord.Interaction,
        recipe: app_commands.Choice[str],
        plots: int
    ):

        pasture, fields = calculate_layout(recipe.value, plots)

        tracker = {}

        for animal, p in pasture.items():
            tracker[animal] = p * 9

        for crop, p in fields.items():
            tracker[crop] = p * 90

        view = FarmTrackerView(recipe.value, tracker)

        await interaction.response.send_message(
            embed=view.build_embed(),
            view=view
        )