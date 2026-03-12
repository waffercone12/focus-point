import discord
from discord import app_commands

from core.calculator import calculate_layout
from core.data_loader import RECIPES
from utils.embed_builder import build_layout_embed


def register(tree):

    recipe_choices = [
        app_commands.Choice(name=k, value=k)
        for k in RECIPES.keys()
    ][:25]

    @tree.command(name="optimize", description="Sustainable island farm layout")
    @app_commands.choices(recipe=recipe_choices)
    @app_commands.describe(
        recipe="Select recipe",
        plots="Total island plots"
    )
    async def optimize(
        interaction: discord.Interaction,
        recipe: app_commands.Choice[str],
        plots: int
    ):

        pasture, fields = calculate_layout(recipe.value, plots)

        embed = build_layout_embed(
            recipe.value,
            pasture,
            fields
        )

        await interaction.response.send_message(embed=embed)