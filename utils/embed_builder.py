import discord
from datetime import datetime, timezone


def build_layout_embed(recipe, pasture, fields, footer_text="Layout generated"):

    embed = discord.Embed(
        title=f"Island Layout — {recipe}",
        color=0x9b59b6,
        timestamp=datetime.now(timezone.utc)
    )

    pasture_text = "\n".join(
        f"{animal}: {plots} plots"
        for animal, plots in pasture.items()
    ) or "None"

    field_text = "\n".join(
        f"{crop}: {plots} plots"
        for crop, plots in fields.items()
    ) or "None"

    embed.add_field(name="🐄 Pasture Plots", value=pasture_text, inline=False)
    embed.add_field(name="🌾 Field Plots", value=field_text, inline=False)

    embed.set_footer(text=footer_text)

    return embed