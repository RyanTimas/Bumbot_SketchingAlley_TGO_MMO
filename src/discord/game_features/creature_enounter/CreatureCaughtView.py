import discord
from discord.ui import Button, Modal, TextInput, Select

from src.commons.AsyncBlocking import run_serialized_blocking
from src.commons.CommonDecorators import retry_on_ssl_error
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_enounter import CreatureEmbedHandler
from src.discord.handlers.AvatarUnlockHandler.AvatarUnlockHandler import check_for_secret_avatars
from src.discord.handlers.CreatureReleaseService.CreatureReleaseService import CreatureReleaseService
from src.discord.objects.TGOPlayer import TGOPlayer


class CreatureCaughtView(discord.ui.View):
    def __init__(self, user_id: int, creature_catch_id: int, successful_catch_embed_handler: CreatureEmbedHandler =None, successful_catch_message: discord.Message= None, message_author: TGOPlayer = None, display_creature_labels: list = None):
        super().__init__(timeout=None)

        self.message_author: TGOPlayer = message_author or get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id)
        self.creature_catch_id = creature_catch_id

        # Keep a reference to the original message and embed handler so we can update the embed with the nickname when it's set
        self.successful_catch_message = successful_catch_message
        self.successful_catch_embed_handler = successful_catch_embed_handler

        # handles display creature index state for the view - this is needed to properly update the db and view when changing display creature
        self.display_index = None
        self.display_creature_ids = [getattr(self.message_author, f'creature_slot_id_{i}') for i in range(1, 7)]
        self.original_display_creature_ids = [getattr(self.message_author, f'creature_slot_id_{i}') for i in range(1, 7)]
        self.display_creature_labels = display_creature_labels or [f"{index + 1} - [EMPTY]" for index in range(6)]

        self.view_disabled = False

        # region build view
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
        # endregion


    ''' ---- VIEW ITEM COMPONENTS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- '''
    # region VIEW ITEMS
    # region BUTTONS
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

            # check if the user has selected a display index from the dropdown
            if self.display_index is None:
                await interaction.followup.send(f"You gotta pick a display index first", ephemeral=True)
                return

            # check if the selected display index is already occupied by another creature, and if so, remove that creature from the display slot
            self.display_creature_ids[self.display_index] = self.creature_catch_id
            self.display_creature_labels = await run_serialized_blocking(self._set_display_creature, creature_id=self.creature_catch_id, user_id=interaction.user.id, display_index=self.display_index,)

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
            self.view_disabled = True
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
            # disable the view so the user can't double release a creature
            for item in self.children:
                item.disabled = True


            # figure out how much currency the user should earn from releasing the creature and which items they earned, then update the db accordingly
            currency_earned, earned_items = await CreatureReleaseService.release_creatures_with_rewards(user_id=self.message_author.user_id, creature_ids=[self.creature_catch_id], interaction=interaction)

            # set the user's creature to released in the db
            release_results_file = await run_serialized_blocking(CreatureReleaseService.create_release_results_file, target_user=self.message_author, currency_earned=currency_earned, earned_items=earned_items, count_released=1,)

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
            is_favorite = await run_serialized_blocking( self._toggle_favorite, self.creature_catch_id,)
            self.refresh_view()
            await interaction.edit_original_response(view=self)
            await interaction.followup.send(f"Creature {'favorited' if is_favorite else 'unfavorited'}!", ephemeral=True)
        return callback
    # endregion

    # region MODALS
    def create_nickname_modal(self):
        user_details_modal = Modal(title="Update Profile Details")
        user_details_modal.add_item(self.nickname_input)

        user_details_modal.on_submit = self.nickname_modal_on_submit()
        return user_details_modal
    def nickname_modal_on_submit(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()

            # update the nickname in the db and refresh the view
            nickname = self.nickname_input.value
            await run_serialized_blocking(self._update_nickname, self.creature_catch_id, nickname,)
            self.nickname_input = TextInput(label="Nickname", default=nickname, placeholder="Enter a nickname for your creature", max_length=50, required=True)
            await check_for_secret_avatars(user_id=interaction.user.id, nickname=nickname, interaction=interaction)

            # edit original caught creature notif to show nickname
            await interaction.followup.send(f"Nickname set to: {nickname}", ephemeral=True)
            if self.successful_catch_message and self.successful_catch_embed_handler:
                embed = await run_serialized_blocking(self._generate_nickname_embed, user_id=interaction.user.id, nickname=nickname,)
                await self.successful_catch_message.edit(embed=embed)
        return callback
    # endregion

    # region DROPDOWNS
    def create_display_creature_index_dropdown(self, row=1):
        options = []
        for index, display_creature_id in enumerate(self.display_creature_ids):
            label = self.display_creature_labels[index]
            options.append(discord.SelectOption(label=label, value=str(index)))

        dropdown = Select(placeholder="Choose Display Slot", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.display_creature_index_dropdown_callback()
        return dropdown
    def display_creature_index_dropdown_callback(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            self.display_index = int(interaction.data["values"][0])
        return callback
    # endregion
    # endregion

    ''' ---- VIEW STATE FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- '''
    # region VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        return
    def rebuild_view(self):
        self.clear_items()  # Clear existing items first
        self.add_item(self.favorite_button)

        self.add_item(self.release_confirmation_button if self.view_disabled else self.release_button)

        self.add_item(self.nickname_button)
        self.add_item(self.display_creature_button)
        self.add_item(self.create_display_creature_index_dropdown(row=2))  # Still create fresh since content changes
    # endregion

    ''' ---- DB INTERACTIONS FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- '''
    # region DB INTERACTIONS

    # remove the creature from the display slot if it is currently displayed in any of the slots
    def handle_existing_display_creature_removal(self, creature_id: int, user_id: int):
        for index, id in enumerate(self.display_creature_ids):
            if id == creature_id:
                get_tgommo_db_handler().update_creature_display_index(user_id=user_id, creature_id=-1, display_index=index)
                self.display_creature_ids[index] = -1
                return

    # update the display creature index in the db and return the updated display creature labels
    def _set_display_creature(self, creature_id: int, user_id: int, display_index: int):
        # pull the current display creature ids from the db to ensure we have the latest state
        current_display_ids = [getattr(get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id), f'creature_slot_id_{i}') for i in range(1, 7)]

        # remove the creature from any existing display slot if it is currently displayed in any of the slots
        for index, current_id in enumerate(current_display_ids):
            if current_id == creature_id:
                get_tgommo_db_handler().update_creature_display_index(user_id=user_id, creature_id=-1, display_index=index,)

        # update the db with the new display creature index
        get_tgommo_db_handler().update_creature_display_index(user_id=user_id, creature_id=creature_id, display_index=display_index,)

        # update the local display_creature_ids list to reflect the new state
        display_ids = list(current_display_ids)
        display_ids[display_index] = creature_id
        labels = []
        for index, display_id in enumerate(display_ids):
            creature = get_tgommo_db_handler().get_user_creature_by_catch_id(display_id) if display_id and display_id != -1 else None
            labels.append(f"{index + 1} - [EMPTY]" if creature is None else f"{index + 1} - {creature.nickname} ({creature.name})")
        return labels

    # Update the nickname of a creature in the database
    @staticmethod
    def _update_nickname(creature_catch_id: int, nickname: str):
        return get_tgommo_db_handler().update_creature_nickname(creature_catch_id, nickname)

    # Load the user's profile and display creature labels for the view
    @staticmethod
    def load_view_state(user_id: int):
        profile = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id)
        display_ids = [getattr(profile, f'creature_slot_id_{i}') for i in range(1, 7)]
        labels = []
        for index, display_id in enumerate(display_ids):
            creature = get_tgommo_db_handler().get_user_creature_by_catch_id(display_id) if display_id and display_id != -1 else None
            labels.append(f"{index + 1} - [EMPTY]" if creature is None else f"{index + 1} - {creature.nickname} ({creature.name})")
        return profile, labels

    # Toggle the favorite status of a creature in the database
    @staticmethod
    def _toggle_favorite(creature_catch_id: int):
        creature = get_tgommo_db_handler().get_user_creature_by_catch_id(creature_catch_id, convert_to_object=True)
        new_value = not creature.is_favorite
        get_tgommo_db_handler().update_user_creature_set_is_favorite(creature_ids=[creature_catch_id], is_favorite=new_value,)
        return new_value

    # Generate a new embed for the successful catch message with the updated nickname
    def _generate_nickname_embed(self, user_id: int, nickname: str):
        return self.successful_catch_embed_handler.generate_catch_embed(catch_user=get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id), nickname=nickname,)[0]

    # endregion