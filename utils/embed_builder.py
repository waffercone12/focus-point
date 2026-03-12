import discord


def build_layout_embed(recipe, pasture, fields):

    embed = discord.Embed(
        title=f"Island Layout — {recipe}",
        color=0x9b59b6
    )

    pasture_text = "\n".join(
        f"{animal}: {plots} plots"
        for animal, plots in pasture.items()
    ) or "None"

    field_text = "\n".join(
        f"{crop}: {plots} plots"
        for crop, plots in fields.items()
    ) or "None"

    embed.add_field(
        name="🐄 Pasture Plots",
        value=pasture_text,
        inline=False
    )

    embed.add_field(
        name="🌾 Field Plots",
        value=field_text,
        inline=False
    )

    return embed