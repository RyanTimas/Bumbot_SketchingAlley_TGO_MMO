import discord
from discord.ui import Button, Modal, TextInput, Select

from src.commons.CommonFunctions import retry_on_ssl_error
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_enounter import CreatureEmbedHandler
from src.discord.handlers.AvatarUnlockHandler.AvatarUnlockHandler import AvatarUnlockHandler
from src.discord.handlers.CreatureReleaseService.CreatureReleaseService import CreatureReleaseService
from src.discord.objects.TGOPlayer import TGOPlayer


class CreatureCaughtView(discord.ui.View):
    def __init__(self, user_id: int, creature_catch_id: int, successful_catch_embed_handler: CreatureEmbedHandler =None, successful_catch_message: discord.Message= None):
        super().__init__(timeout=None)

        self.message_author: TGOPlayer = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id)
        self.creature_catch_id = creature_catch_id

        # Keep a reference to the original message and embed handler so we can update the embed with the nickname when it's set
        self.successful_catch_message = successful_catch_message
        self.successful_catch_embed_handler = successful_catch_embed_handler

        # handles display creature index state for the view - this is needed to properly update the db and view when changing display creature
        self.display_index = None
        self.display_creature_ids = [getattr(self.message_author, f'creature_slot_id_{i}') for i in range(1, 7)]
        self.original_display_creature_ids = [getattr(self.message_author, f'creature_slot_id_{i}') for i in range(1, 7)]

        # use
        self._release_confirmed = False

        # VIEW COMPONENTS
        # buttons
        self.favorite_button = self.create_favorite_button(row=0)
        self.release_button = self.create_release_button(row=0)
        self.release_confirmation_button = self.create_release_confirmation_button(row=0)
        self.nickname_button = self.create_nickname_button(row=1)
        self.display_creature_button = self.create_display_creature_button(row=1)

        # modals
        self.nickname_input = TextInput(label="Nickname", placeholder="Enter nickname (12 chars max)", max_length=20, required=True)
        self.display_creature_index_input = TextInput(label="DisplayCreatureIndex", placeholder="Enter index of display slot (1-6)", max_length=1, required=True)

        # add items to view
        self.refresh_view()


    # CREATE BUTTONS
    def create_nickname_button(self, row=0):
        button = Button(label="Set Nickname", style=discord.ButtonStyle.red, row=row)
        button.callback = self.nickname_button_callback()
        return button
    def nickname_button_callback(self):
        async def callback(interaction: discord.Interaction):
            modal = self.create_nickname_modal()
            await interaction.response.send_modal(modal)
        return callback

    def create_display_creature_button(self, row=0):
        button = Button(label="Set as display creature", style=discord.ButtonStyle.red, row=row)
        button.callback = self.display_creature_button_callback()
        return button
    def display_creature_button_callback(self):
        @retry_on_ssl_error()
        async def callback(interaction):
            await interaction.response.defer()
            if self.display_index is None:
                await interaction.followup.send(f"You gotta pick a display index first", ephemeral=True)
                return
            self.handle_existing_display_creature_removal(creature_id=self.creature_catch_id, user_id=interaction.user.id)
            get_tgommo_db_handler().update_creature_display_index(user_id=interaction.user.id, creature_id=self.creature_catch_id, display_index=self.display_index)
            self.display_creature_ids[self.display_index] = self.creature_catch_id
            self.refresh_view()
            await interaction.edit_original_response(view=self)
            await interaction.followup.send(f"Display index set to: {self.display_index + 1}", ephemeral=True)
        return callback


    def create_release_button(self, row=0):
        button = Button(label="Release Creature", style=discord.ButtonStyle.success, emoji="🗑️", row=row)
        button.callback = self.release_button_callback()
        return button
    def release_button_callback(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            self._release_confirmed = True
            self.refresh_view()
            await interaction.edit_original_response(view=self)
        return callback

    def create_release_confirmation_button(self, row=0):
        button = Button(label="ARE YOU SURE? THIS CANNOT BE UNDONE!", style=discord.ButtonStyle.danger, emoji="⚠️", row=row)
        button.callback = self.release_confirmation_callback()
        return button
    def release_confirmation_callback(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            self.handle_existing_display_creature_removal(creature_id=self.creature_catch_id, user_id=self.message_author.user_id)
            currency_earned, earned_items = await CreatureReleaseService.release_creatures_with_rewards(user_id=self.message_author.user_id, creature_ids=[self.creature_catch_id], interaction=interaction)
            if not currency_earned:
                await interaction.followup.send("Failed to release creature", ephemeral=True)
                return
            for item in self.children:
                item.disabled = True
            release_results_file = CreatureReleaseService.create_release_results_file(target_user=get_tgommo_db_handler().get_user_profile_by_user_id(self.message_author.user_id), currency_earned=currency_earned, earned_items=earned_items, count_released=1)
            await interaction.edit_original_response(view=self)
            await interaction.followup.send("Released creature successfully!", file=release_results_file, ephemeral=True)
        return callback

    def create_favorite_button(self, row=0):
        button = Button(label="Favorite", style=discord.ButtonStyle.success, emoji="❤️", row=row)
        button.callback = self.favorite_button_callback()
        return button
    def favorite_button_callback(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            creature = get_tgommo_db_handler().get_user_creature_by_catch_id(self.creature_catch_id, convert_to_object=True)
            get_tgommo_db_handler().update_user_creature_set_is_favorite(creature_ids=[self.creature_catch_id, ], is_favorite=not creature.is_favorite)
            self.refresh_view()
            await interaction.edit_original_response(view=self)
            await interaction.followup.send(f"Creature {'favorited' if not creature.is_favorite else 'unfavorited'}!", ephemeral=True)
        return callback

    # CREATE MODALS
    def create_nickname_modal(self):
        user_details_modal = Modal(title="Update Profile Details")
        user_details_modal.add_item(self.nickname_input)

        user_details_modal.on_submit = self.nickname_modal_on_submit()
        return user_details_modal
    def nickname_modal_on_submit(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            get_tgommo_db_handler().update_creature_nickname(self.creature_catch_id, self.nickname_input.value)
            self.nickname_input = TextInput(label="Nickname", default=self.nickname_input.value, placeholder="Enter a nickname for your creature", max_length=50, required=True)
            await AvatarUnlockHandler(user_id=interaction.user.id, nickname=self.nickname_input.value, interaction=interaction).check_avatar_unlock_conditions()
            await interaction.followup.send(f"Nickname set to: {self.nickname_input.value}", ephemeral=True)
            # edit original caught creature notif to show nickname
            await self.successful_catch_message.edit(embed=self.successful_catch_embed_handler.generate_catch_embed(nickname=self.nickname_input.value)[0])
        return callback

    # CREATE DROPDOWNS
    def create_display_creature_index_dropdown(self, row=1):
        options = []
        for index, display_creature_id in enumerate(self.display_creature_ids):
            creature = get_tgommo_db_handler().get_user_creature_by_catch_id(display_creature_id) if display_creature_id and display_creature_id != -1 else None

            label = f"{index+1} - [EMPTY]" if creature is None else f"{index+1} - {creature.nickname} ({creature.name})"
            options.append(discord.SelectOption(label=label, value=str(index)))

        dropdown = Select(placeholder="Choose Display Slot", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.display_creature_index_dropdown_callback()
        return dropdown
    def display_creature_index_dropdown_callback(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            self.display_index = int(interaction.data["values"][0])
        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        return
    def rebuild_view(self):
        self.clear_items()  # Clear existing items first
        self.add_item(self.favorite_button)

        self.add_item(self.release_confirmation_button if self._release_confirmed else self.release_button)

        self.add_item(self.nickname_button)
        self.add_item(self.display_creature_button)
        self.add_item(self.create_display_creature_index_dropdown(row=2))  # Still create fresh since content changes

    # MISC FUNCTIONS
    def handle_existing_display_creature_removal(self, creature_id: int, user_id: int):
        for index, id in enumerate(self.display_creature_ids):
            if id == creature_id:
                get_tgommo_db_handler().update_creature_display_index(user_id=user_id, creature_id=-1, display_index=index)
                self.display_creature_ids[index] = -1
                return