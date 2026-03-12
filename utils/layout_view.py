import discord
from datetime import datetime, timezone
from utils.embed_builder import build_layout_embed


class LayoutView(discord.ui.View):

    def __init__(self, recipe, pasture, fields):
        super().__init__(timeout=None)

        self.recipe = recipe
        self.pasture = pasture
        self.fields = fields

        # track completed rows
        self.completed = set()

    def strike(self, text):
        return f"~~{text}~~"

    def generate_table(self):

        rows = []

        for animal, plots in self.pasture.items():
            rows.append((animal, plots))

        for crop, plots in self.fields.items():
            rows.append((crop, plots))

        table = "Resource        Plots   Status\n"
        table += "--------------------------------\n"

        for name, plots in rows:

            if name in self.completed:
                table += f"{self.strike(name):<14}{self.strike(str(plots)):<8}✅\n"
            else:
                table += f"{name:<14}{plots:<8}⬜\n"

        return table

    def build_embed(self):

        embed = discord.Embed(
            title=f"Island Layout — {self.recipe}",
            color=0x9b59b6,
            timestamp=datetime.now(timezone.utc)
        )

        table = self.generate_table()

        embed.description = f"```\n{table}\n```"

        embed.set_footer(text="Layout updated")

        return embed

    # MARK ALL DONE BUTTON

    @discord.ui.button(label="Mark Entire Layout Done", style=discord.ButtonStyle.success)
    async def mark_all_done(self, interaction: discord.Interaction, button: discord.ui.Button):

        for k in list(self.pasture.keys()) + list(self.fields.keys()):
            self.completed.add(k)

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # RESET BUTTON

    @discord.ui.button(label="Reset", style=discord.ButtonStyle.danger)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.completed.clear()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )