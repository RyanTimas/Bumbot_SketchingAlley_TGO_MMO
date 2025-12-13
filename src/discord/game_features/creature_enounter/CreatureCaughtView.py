import discord
from discord.ui import Button, Modal, TextInput, Select

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_enounter import CreatureEmbedHandler
from src.discord.general.handlers.AvatarUnlockHandler import AvatarUnlockHandler
from src.discord.handlers.CreatureReleaseService.CreatureReleaseService import CreatureReleaseService
from src.discord.objects.TGOPlayer import TGOPlayer


class CreatureCaughtView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, creature_id: int, successful_catch_embed_handler: CreatureEmbedHandler =None, successful_catch_message: discord.Message= None):
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
        self.refresh_view()


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
        if self.display_index is None:
            await interaction.response.send_message(f"You gotta pick a display index first", ephemeral=True)
            return

        # if creature was already set as display creature, remove it from the display list
        for index, id in enumerate(self.display_creature_ids):
            if id == self.creature_id:
                get_tgommo_db_handler().update_creature_display_index(user_id=interaction.user.id,creature_id=self.original_display_creature_ids[index], display_index=index)

        get_tgommo_db_handler().update_creature_display_index(user_id=interaction.user.id, creature_id=self.creature_id, display_index=self.display_index)

        self.display_creature_ids[self.display_index] = self.creature_id
        await interaction.response.send_message(f"Display index set to: {self.display_index+1}", ephemeral=True)

    def create_release_button(self):
        button = Button(label="Release Creature", style=discord.ButtonStyle.danger, emoji="🗑️")
        button.callback = self.release_button_callback
        return button

    async def release_button_callback(self, interaction: discord.Interaction):
        # Remove from display slots if present
        for index, id in enumerate(self.display_creature_ids):
            if id == self.creature_id:
                get_tgommo_db_handler().update_creature_display_index(user_id=interaction.user.id, creature_id=None, display_index=index)

        currency_earned, earned_items = await CreatureReleaseService.release_creatures_with_rewards(user_id=self.interaction.user.id, creature_ids=[self.creature_id], interaction=interaction)

        if not currency_earned:
            await interaction.response.send_message("Failed to release creature", ephemeral=True)
            return

        # Disable all buttons and create results file
        for item in self.children:
            item.disabled = True

        release_results_file = CreatureReleaseService.create_release_results_file(user=self.interaction.user, currency_earned=currency_earned, earned_items=earned_items, count_released=1)

        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Released creature successfully!", file=release_results_file, ephemeral=True)

    def create_favorite_button(self):
        creature = get_tgommo_db_handler().get_creature_by_catch_id(self.creature_id, convert_to_object=True)
        is_favorited = creature.is_favorite if creature else False

        label = "Unfavorite" if is_favorited else "Favorite"
        style = discord.ButtonStyle.secondary if is_favorited else discord.ButtonStyle.success
        emoji = "💔" if is_favorited else "❤️"

        button = Button(label=label, style=style, emoji=emoji)
        button.callback = self.favorite_button_callback
        return button
    async def favorite_button_callback(self, interaction: discord.Interaction):
        creature = get_tgommo_db_handler().get_creature_by_catch_id(self.creature_id, convert_to_object=True)

        # Toggle favorite status
        get_tgommo_db_handler().update_user_creature_set_is_favorite(creature_ids=[self.creature_id,], is_favorite=not creature.is_favorite)

        # Refresh view to update button state
        self.refresh_view()

        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"Creature {"favorited" if not creature.is_favorite else "unfavorited"}!", ephemeral=True)


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
            creature = get_tgommo_db_handler().get_creature_by_catch_id(display_creature_id, convert_to_object=True)

            label = f"{index+1} - [EMPTY]" if creature is None else f"{index+1} - {creature.nickname} ({creature.name})"
            options.append(discord.SelectOption(label=label, value=str(index)))

        dropdown = Select(placeholder="Choose Display Slot", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.display_creature_index_dropdown_callback
        return dropdown
    async def display_creature_index_dropdown_callback(self, interaction: discord.Interaction):
        self.display_index = int(interaction.data["values"][0])
        await interaction.response.defer()


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        return
    def rebuild_view(self):
        self.clear_items()  # Clear existing items first
        self.add_item(self.create_nickname_button())
        self.add_item(self.create_display_creature_index_dropdown())
        self.add_item(self.create_display_creature_button())
        self.add_item(self.create_favorite_button())
        self.add_item(self.create_release_button())