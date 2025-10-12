import discord
from discord.ui import Button, Modal, TextInput, Select

from src.commons.CommonFunctions import retry_on_ssl_error
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.embeds import CreatureEmbedHandler
from src.discord.handlers.AvatarUnlockHandler import AvatarUnlockHandler
from src.discord.objects.TGOPlayer import TGOPlayer


class CreatureCaughtView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, creature_id: int, successful_catch_embed_handler:CreatureEmbedHandler =None, successful_catch_message: discord.Message= None):
        super().__init__(timeout=None)

        self.creature_id = creature_id
        self.interaction = interaction
        self.display_index = None

        self.successful_catch_message = successful_catch_message
        self.successful_catch_embed_handler = successful_catch_embed_handler

        self.user_profile:TGOPlayer = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.interaction.user.id, convert_to_object=True)
        self.display_creature_ids = [self.user_profile.creature_slot_id_1, self.user_profile.creature_slot_id_2, self.user_profile.creature_slot_id_3, self.user_profile.creature_slot_id_4, self.user_profile.creature_slot_id_5, self.user_profile.creature_slot_id_6, ]
        self.original_display_creature_ids = [self.user_profile.creature_slot_id_1, self.user_profile.creature_slot_id_2, self.user_profile.creature_slot_id_3, self.user_profile.creature_slot_id_4, self.user_profile.creature_slot_id_5, self.user_profile.creature_slot_id_6, ]

        # modals
        self.nickname_input = TextInput(label="Nickname", placeholder="Enter nickname (12 chars max)", max_length=20, required=True)
        self.display_creature_index_input = TextInput(label="DisplayCreatureIndex", placeholder="Enter index of display slot (1-6)", max_length=1, required=True)

        # add items to view
        self.add_item(self.create_nickname_button())
        self.add_item(self.create_display_creature_index_dropdown())
        self.add_item(self.create_display_creature_button())

    # CREATE BUTTONS
    def create_nickname_button(self):
        button = Button(label="Set Nickname", style=discord.ButtonStyle.red)
        button.callback = self.nickname_button_callback
        return button
    async def nickname_button_callback(self, interaction: discord.Interaction):
        modal = self.create_nickname_modal()
        await interaction.response.send_modal(modal)

    def create_display_creature_button(self):
        button = Button(label="Set as display creature", style=discord.ButtonStyle.red)
        button.callback = self.display_creature_button_callback
        return button
    async def display_creature_button_callback(self, interaction: discord.Interaction):

        # if creature was already set as display creature, remove it from the display list
        for index, id in enumerate(self.display_creature_ids):
            if id == self.creature_id:
                get_tgommo_db_handler().update_creature_display_index(user_id=interaction.user.id,creature_id=self.original_display_creature_ids[index], display_index=index)

        get_tgommo_db_handler().update_creature_display_index(user_id=interaction.user.id, creature_id=self.creature_id, display_index=self.display_index)

        self.display_creature_ids[self.display_index] = self.creature_id
        await interaction.response.send_message(f"Display index set to: {self.display_index+1}", ephemeral=True)


    # CREATE MODALS
    def create_nickname_modal(self):
        user_details_modal = Modal(title="Update Profile Details")
        user_details_modal.add_item(self.nickname_input)

        user_details_modal.on_submit = self.nickname_modal_on_submit
        return user_details_modal
    async def nickname_modal_on_submit(self, interaction: discord.Interaction):
        get_tgommo_db_handler().update_creature_nickname(self.creature_id, self.nickname_input.value)
        self.nickname_input = TextInput(label="Nickname", default=self.nickname_input.value, placeholder="Enter a nickname for your creature", max_length=50, required=True)
        await AvatarUnlockHandler(user_id=interaction.user.id, nickname=self.nickname_input.value, interaction=interaction).check_avatar_unlock_conditions()
        await interaction.response.send_message(f"Nickname set to: {self.nickname_input.value}", ephemeral=True)

        # edit original caught creature notif to show nickname
        await self.successful_catch_message.edit(embed=self.successful_catch_embed_handler.generate_catch_embed(nickname=self.nickname_input.value)[0])


    # CREATE DROPDOWNS
    def create_display_creature_index_dropdown(self, row=1):
        options = []
        for index, display_creature_id in enumerate(self.display_creature_ids):
            creature_info = get_tgommo_db_handler().get_creature_by_catch_id(display_creature_id)

            label = f"{index+1} - [EMPTY]" if creature_info is None else f"{index+1} - {creature_info[0]} ({creature_info[1]})"
            options.append(discord.SelectOption(label=label, value=str(index)))

        dropdown = Select(placeholder="Choose Display Slot", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.display_creature_index_dropdown_callback
        return dropdown
    async def display_creature_index_dropdown_callback(self, interaction: discord.Interaction):
        self.display_index = int(interaction.data["values"][0])
        await interaction.response.defer()