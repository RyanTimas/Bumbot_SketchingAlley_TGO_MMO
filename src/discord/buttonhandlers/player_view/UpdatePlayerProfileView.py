import asyncio

import discord
from discord.ext.commands import param
from discord.ui import Modal, TextInput, Button, Select

from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOPlayer import TGOPlayer


class UpdatePlayerProfileView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, user_id: int, player: TGOPlayer):
        super().__init__(timeout=None)

        # LOAD VARIABLES
        self.user_id = user_id
        self.interaction = interaction

        self.user_id = user_id
        self.display_name = player.nickname

        self.avatar_id = player.avatar_id
        self.background_id = player.background_id

        self.creature_id_1 = player.creature_slot_id_1
        self.creature_id_2 = player.creature_slot_id_2
        self.creature_id_3 = player.creature_slot_id_3
        self.creature_id_4 = player.creature_slot_id_4
        self.creature_id_5 = player.creature_slot_id_5
        self.creature_id_6 = player.creature_slot_id_6

        self.currency = player.currency
        self.available_catches = player.available_catches
        self.rod_level = player.rod_level
        self.rod_amount = player.rod_amount
        self.trap_level = player.trap_level
        self.trap_amount = player.trap_amount


        # LOAD VIEW COMPONENTS
        # buttons
        update_profile_button = self.create_update_profile_button(row=3)
        save_changes_button = self.create_save_changes_button(row=3)

        # text inputs
        self.display_name_input = TextInput(label="DisplayName", placeholder="Set your display name", max_length=20, required=False)
        self.display_creature_1_input = TextInput(label="Display Creature 1", placeholder="Set the ID for which creature you would like to display in index 1", max_length=20, required=False)
        self.display_creature_2_input = TextInput(label="Display Creature 2", placeholder="Set the ID for which creature you would like to display in index 2", max_length=20, required=False)
        self.display_creature_3_input = TextInput(label="Display Creature 3", placeholder="Set the ID for which creature you would like to display in index 3", max_length=20, required=False)
        self.display_creature_4_input = TextInput(label="Display Creature 4", placeholder="Set the ID for which creature you would like to display in index 4", max_length=20, required=False)
        self.display_creature_5_input = TextInput(label="Display Creature 5", placeholder="Set the ID for which creature you would like to display in index 5", max_length=20, required=False)
        self.display_creature_6_input = TextInput(label="Display Creature 6", placeholder="Set the ID for which creature you would like to display in index 6", max_length=20, required=False)
        # modals
        self.update_profile_modal = self.create_user_details_modal()

        # dropdowns
        avatar_picker_dropdown = self.create_avatar_picker_dropdown(row=1)
        background_picker_dropdown = self.create_background_picker_dropdown(row=2)


        # ADD COMPONENTS TO VIEW
        self.add_item(avatar_picker_dropdown)                 # row 1
        self.add_item(background_picker_dropdown)        # row 2

        self.add_item(update_profile_button)                    # row 3
        self.add_item(save_changes_button)                    # row 3


    # CREATE BUTTONS
    def create_update_profile_button(self, row=0):
        button = Button(label="Change Profile", style=discord.ButtonStyle.blurple, row=row)
        button.callback = self.update_profile_button_callback
        return button
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def update_profile_button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.update_profile_modal)

    def create_save_changes_button(self, row=0):
        button = Button(label="Save Changes", style=discord.ButtonStyle.green, row=row)
        button.callback = self.save_changes_button_callback
        return button
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def save_changes_button_callback(self, interaction: discord.Interaction):
        params = (self.display_name,self.avatar_id,self.background_id,self.creature_id_1,self.creature_id_2,self.creature_id_3,self.creature_id_4,self.creature_id_5,self.creature_id_6, self.currency,self.available_catches, self.rod_level, self.rod_amount,self.trap_level,self.trap_amount, self.user_id)
        get_tgommo_db_handler().update_user_profile(params=params)

        await interaction.response.send_message("Changes successfully saved!", ephemeral=True)

    # CREATE MODALS
    def create_user_details_modal(self):
        user_details_modal = Modal(title="Update Profile Details")

        user_details_modal.add_item(self.display_name_input)
        user_details_modal.add_item(self.display_creature_1_input)
        user_details_modal.add_item(self.display_creature_2_input)
        user_details_modal.add_item(self.display_creature_3_input)
        user_details_modal.add_item(self.display_creature_4_input)
        # user_details_modal.add_item(self.display_creature_5_input)
        # user_details_modal.add_item(self.display_creature_6_input)

        user_details_modal.on_submit = self.user_details_modal_on_submit
        return user_details_modal
    async def user_details_modal_on_submit(self, interaction: discord.Interaction):
        self.display_name = self.display_name_input.value if self.display_name_input.value != '' else self.display_name
        self.creature_id_1 = self.display_creature_1_input.value if self.display_creature_1_input.value != '' else self.creature_id_1
        self.creature_id_2 = self.display_creature_2_input.value if self.display_creature_2_input.value != '' else self.creature_id_2
        self.creature_id_3 = self.display_creature_3_input.value if self.display_creature_3_input.value != '' else self.creature_id_3
        self.creature_id_4 = self.display_creature_4_input.value if self.display_creature_4_input.value != '' else self.creature_id_4
        self.creature_id_5 = self.display_creature_5_input.value if self.display_creature_5_input.value != '' else self.creature_id_5
        self.creature_id_6 = self.display_creature_6_input.value if self.display_creature_6_input.value != '' else self.creature_id_6

        await interaction.response.send_message(f"Successfully set avatar to {self.avatar_id}", ephemeral=True)
        # todo: edit current message to reflect changes


    # CREATE DROPDOWNS
    def create_avatar_picker_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Avatar {i}", value=str(i)) for i in range(1, 3)]
        dropdown = Select(placeholder="Choose Avatar", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    async def avatar_dropdown_callback(self, interaction: discord.Interaction):
        # Access the selected value from the interaction
        self.avatar_id = int(interaction.data["values"][0])
        await interaction.response.send_message(f"Successfully set avatar to {self.avatar_id}", ephemeral=True)


    def create_background_picker_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Background {i}", value=str(i)) for i in range(1, 2)]
        dropdown = Select(placeholder="Choose Background Style", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    async def background_dropdown_callback(self, interaction: discord.Interaction):
        # Access the selected value from the interaction
        self.background_id = int(interaction.data["values"][0])
        await interaction.response.send_message(f"Successfully set avatar to {self.background_id}", ephemeral=True)

    def create_creature_picker_dropdown(self):
        get_tgommo_db_handler().get_creature_collection_by_user(self.user_id)


        options = [discord.SelectOption(label=f"Background {i}", value=str(i)) for i in range(1, 2)]
        dropdown = Select(placeholder="Choose Background Style", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    async def creature_picker_dropdown_callback(self, interaction: discord.Interaction):
        self.background_id = int(interaction.data["values"][0])
        await interaction.response.send_message(f"Successfully set avatar to {self.background_id}", ephemeral=True)
