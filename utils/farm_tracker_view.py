import discord
from datetime import datetime, timezone


class FarmTrackerView(discord.ui.View):

    def __init__(self, recipe, tracker):
        super().__init__(timeout=None)

        self.recipe = recipe
        self.tracker = tracker
        self.completed = set()

        for name in tracker.keys():
            self.add_item(self.create_button(name))

    def strike(self, text):
        return f"~~{text}~~"

    # -------- Progress Bar --------

    def progress_bar(self):

        total = len(self.tracker)
        done = len(self.completed)

        if total == 0:
            return "░░░░░ 0%"

        percent = int((done / total) * 100)

        bars = 5
        filled = int((done / total) * bars)

        bar = "█" * filled + "░" * (bars - filled)

        return f"{bar} {percent}%"

    # -------- Table --------

    def build_table(self):

        table = "Resource        Required   Done\n"
        table += "----------------------------------\n"

        for name, qty in self.tracker.items():

            if name in self.completed:
                table += f"{self.strike(name):<14}{self.strike(str(qty)):<10}✅\n"
            else:
                table += f"{name:<14}{qty:<10}⬜\n"

        return table

    # -------- Embed --------

    def build_embed(self):

        embed = discord.Embed(
            title=f"Island Farm Tracker — {self.recipe}",
            color=0x2ecc71,
            timestamp=datetime.now(timezone.utc)
        )

        table = self.build_table()

        embed.description = f"```\n{table}\n```"

        total = len(self.tracker)
        done = len(self.completed)

        embed.add_field(
            name="Progress",
            value=f"{self.progress_bar()}\n{done} / {total} tasks completed",
            inline=False
        )

        embed.set_footer(text="Tracker updated")

        return embed

    # -------- Dynamic Buttons --------

    def create_button(self, name):

        button = discord.ui.Button(
            label=name,
            style=discord.ButtonStyle.secondary
        )

        async def callback(interaction: discord.Interaction):

            self.completed.add(name)

            await interaction.response.edit_message(
                embed=self.build_embed(),
                view=self
            )

        button.callback = callback
        return button

    # -------- Mark All Done --------

    @discord.ui.button(label="Mark All Done", style=discord.ButtonStyle.success)
    async def mark_all(self, interaction: discord.Interaction, button):

        for name in self.tracker.keys():
            self.completed.add(name)

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # -------- Reset --------

    @discord.ui.button(label="Reset", style=discord.ButtonStyle.danger)
    async def reset(self, interaction: discord.Interaction, button):

        self.completed.clear()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )