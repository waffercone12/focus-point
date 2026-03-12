import discord
from datetime import datetime, timezone
from core.calculator import calculate_layout


# ---------- MODAL: EDIT PLOTS ----------

class PlotModal(discord.ui.Modal, title="Edit Plot Size"):

    plots = discord.ui.TextInput(
        label="Total Island Plots",
        placeholder="Enter new plot count",
        required=True
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):

        try:
            plots = int(self.plots.value)

            pasture, fields = calculate_layout(self.view.recipe, plots)

            self.view.pasture = pasture
            self.view.fields = fields
            self.view.completed.clear()

            self.view.updated_at = datetime.now(timezone.utc)

            await interaction.response.edit_message(
                embed=self.view.build_embed(),
                view=self.view
            )

        except ValueError:
            await interaction.response.send_message(
                "Invalid plot number.",
                ephemeral=True
            )


# ---------- MODAL: ADD RESOURCE ----------

class AddResourceModal(discord.ui.Modal, title="Add Custom Resource"):

    name = discord.ui.TextInput(
        label="Resource Name",
        placeholder="Example: Carrot",
        required=True
    )

    quantity = discord.ui.TextInput(
        label="Required Amount",
        placeholder="Example: 100",
        required=True
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):

        try:
            qty = int(self.quantity.value)

            self.view.custom_resources[self.name.value] = qty

            self.view.updated_at = datetime.now(timezone.utc)

            await interaction.response.edit_message(
                embed=self.view.build_embed(),
                view=self.view
            )

        except ValueError:
            await interaction.response.send_message(
                "Quantity must be a number.",
                ephemeral=True
            )


# ---------- MAIN VIEW ----------

class LayoutView(discord.ui.View):

    def __init__(self, recipe, pasture, fields):
        super().__init__(timeout=None)

        self.recipe = recipe
        self.pasture = pasture
        self.fields = fields

        self.custom_resources = {}

        self.completed = set()

        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at

        # dynamic buttons
        for name in list(pasture.keys()) + list(fields.keys()):
            self.add_item(self.create_toggle_button(name))

    # ---------- Toggle Button ----------

    def create_toggle_button(self, name):

        button = discord.ui.Button(
            label=name,
            style=discord.ButtonStyle.secondary
        )

        async def callback(interaction: discord.Interaction):

            if name in self.completed:
                self.completed.remove(name)
            else:
                self.completed.add(name)

            self.updated_at = datetime.now(timezone.utc)

            await interaction.response.edit_message(
                embed=self.build_embed(),
                view=self
            )

        button.callback = callback
        return button

    # ---------- Progress Bar ----------

    def progress_bar(self):

        total = len(self.pasture) + len(self.fields) + len(self.custom_resources)
        done = len(self.completed)

        if total == 0:
            return "░░░░░ 0%"

        percent = int((done / total) * 100)

        bars = 5
        filled = int((done / total) * bars)

        return "█" * filled + "░" * (bars - filled) + f" {percent}%"

    # ---------- Table Builder ----------

    def build_table(self):

        table = "Resource        Plots/Qty   Status\n"
        table += "--------------------------------------\n"

        resources = {}

        resources.update(self.pasture)
        resources.update(self.fields)
        resources.update(self.custom_resources)

        for name, qty in resources.items():

            if name in self.completed:
                table += f"~~{name}~~{' '*(14-len(name))}~~{qty}~~{' '*(6-len(str(qty)))}✅\n"
            else:
                table += f"{name:<14}{qty:<10}⬜\n"

        return table

    # ---------- Embed Builder ----------

    def build_embed(self):

        embed = discord.Embed(
            title=f"Island Farm Tracker — {self.recipe}",
            color=0x2ecc71,
            timestamp=self.updated_at
        )

        table = self.build_table()

        embed.description = f"```\n{table}\n```"

        total = len(self.pasture) + len(self.fields) + len(self.custom_resources)
        done = len(self.completed)

        embed.add_field(
            name="Progress",
            value=f"{self.progress_bar()}\n{done} / {total} tasks completed",
            inline=False
        )

        embed.set_footer(
            text=f"Created: {self.created_at.strftime('%H:%M:%S')} | Updated: {self.updated_at.strftime('%H:%M:%S')}"
        )

        return embed

    # ---------- Buttons ----------

    @discord.ui.button(label="Edit Plots", style=discord.ButtonStyle.primary)
    async def edit_plots(self, interaction: discord.Interaction, button):

        await interaction.response.send_modal(PlotModal(self))

    @discord.ui.button(label="Add Resource", style=discord.ButtonStyle.secondary)
    async def add_resource(self, interaction: discord.Interaction, button):

        await interaction.response.send_modal(AddResourceModal(self))

    @discord.ui.button(label="Reset", style=discord.ButtonStyle.danger)
    async def reset(self, interaction: discord.Interaction, button):

        self.completed.clear()
        self.updated_at = datetime.now(timezone.utc)

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )