from discord.ui import Select

from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.handlers.CreatureReleaseService.CreatureReleaseService import CreatureReleaseService
from src.discord.handlers.CreatureReleaseService.ReleaseResultImageFactory import ReleaseResultImageFactory
from src.resources.constants.TGO_MMO_constants import *


class CreatureInventoryManagementView(discord.ui.View):
    def __init__(self, message_author, mode, creatures, creature_inventory_image_factory: CreatureInventoryImageFactory, original_message=None, original_view=None, view_state= VIEW_WORKFLOW_STATE_INTERACTION, select_all_enabled=False, show_only_mythics=False, show_only_favorites=False, show_only_nicknames=False):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.mode = mode

        self.creature_inventory_image_factory = creature_inventory_image_factory
        self.release_result_image_factory = ReleaseResultImageFactory(user= message_author)
        self.original_view = original_view
        self.original_message = original_message

        self.creatures = creatures
        self.selected_ids = []

        self.interaction_lock = asyncio.Lock()
        self.view_state = view_state

        self.show_only_mythics = show_only_mythics
        self.show_only_favorites = show_only_favorites
        self.show_only_nicknames = show_only_nicknames
        self.select_all_enabled = select_all_enabled

        # DEFINE VIEW COMPONENTS
        self.selectable_creature_dropdown_1 = self.create_creature_dropdown(row=0, dropdown_num=0)
        self.selectable_creature_dropdown_2 = self.create_creature_dropdown(row=1, dropdown_num=1)
        self.selectable_creature_dropdown_3 = self.create_creature_dropdown(row=2, dropdown_num=2)
        self.selectable_creature_dropdown_4 = self.create_creature_dropdown(row=3, dropdown_num=3)

        self.confirmation_button = self.create_confirmation_button(row=4)
        self.final_confirmation_button_yes = self.create_final_confirmation_button(row=4, is_confirm=True)
        self.final_confirmation_button_no = self.create_final_confirmation_button(row=4, is_confirm=False)
        self.select_all_button = self.create_select_all_button(row=4)
        self.deselect_all_button = self.create_deselect_all_button(row=4)

        self.refresh_view()


    # CREATE BUTTONS
    def create_confirmation_button(self, row=0):
        button = discord.ui.Button(
            label=f"{self.mode} Creatures",
            style=discord.ButtonStyle.blurple,
            row=row
        )

        button.callback = self.confirmation_callback()
        return button
    def confirmation_callback(self, ):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                updated_image = self.reload_creature_inventory_image(image_mode= self.mode, creature_ids_to_update= self.selected_ids)

                self.refresh_view(view_state = VIEW_WORKFLOW_STATE_CONFIRMATION)
                await interaction.followup.send(content=f"You have selected the following creatures. Are you sure you want to {self.mode} them?", files=[updated_image], view=self, ephemeral=True)

        return callback

    def create_final_confirmation_button(self, row=0, is_confirm=True):
        button = discord.ui.Button(
            label=f"Confirm" if is_confirm else "No",
            style=discord.ButtonStyle.green if is_confirm else discord.ButtonStyle.red,
            row=row,
            custom_id=f"final_confirmation_{'yes' if is_confirm else 'no'}"  # Unique custom_id
        )

        button.callback = self.final_confirmation_callback()
        return button
    def final_confirmation_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                # Route to appropriate handler based on mode - release or favorite
                success, final_image_mode, extra_data = await self._handle_release_operation() if self.mode == CREATURE_INVENTORY_MODE_RELEASE else await self._handle_favorite_operation()
                if not success:
                    await interaction.followup.send(content=f"An error occurred while trying to {self.mode} your creatures. Please try again.", ephemeral=True)
                    return

                self.refresh_view(view_state=VIEW_WORKFLOW_STATE_FINALIZED)

                # Handle Response Messages
                # Send success message
                await interaction.followup.send(content=f"You have successfully {self.mode}'d your guys", ephemeral=True)

                # Update original message with refreshed inventory image
                updated_creature_inventory_image = self.reload_creature_inventory_image(refresh_creatures=True, image_mode=CREATURE_INVENTORY_MODE_DEFAULT)
                await self.original_message.edit(content="", attachments=[updated_creature_inventory_image], view=self.original_view)

                # Show release results if releasing
                if final_image_mode == CREATURE_INVENTORY_MODE_RELEASE_RESULTS and extra_data:
                    release_results_image = self.reload_release_results_image(currency_earned=extra_data['currency_earned'], earned_items=extra_data['earned_items'], count_released=len(self.selected_ids))
                    await interaction.followup.send(content="Here are your release rewards:", files=[release_results_image], ephemeral=True)
        return callback
    async def _handle_release_operation(self):
        currency_earned, earned_items  = await CreatureReleaseService.release_creatures_with_rewards(user_id=self.message_author.id, creature_ids=self.selected_ids, interaction=None)

        if not currency_earned:
            return False, None, None
        return True, CREATURE_INVENTORY_MODE_RELEASE_RESULTS, {'currency_earned': currency_earned, 'earned_items': earned_items}
    async def _handle_favorite_operation(self):
        success = get_tgommo_db_handler().update_user_creature_set_is_favorite(creature_ids=self.selected_ids)
        return success, CREATURE_INVENTORY_MODE_DEFAULT, None

    def create_select_all_button(self, row=4):
        button = discord.ui.Button(
            label="Select All",
            style=discord.ButtonStyle.secondary,
            row=row,
            custom_id="select_all_button"
        )
        button.callback = self.select_all_callback
        return button
    async def select_all_callback(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
            return

        dropdowns = [
            (self.selectable_creature_dropdown_1, len(self.creatures) > 0),
            (self.selectable_creature_dropdown_2, len(self.creatures) > 25),
            (self.selectable_creature_dropdown_3, len(self.creatures) > 50),
            (self.selectable_creature_dropdown_4, len(self.creatures) > 75)
        ]

        for dropdown, is_present in dropdowns:
            if is_present and dropdown.options:
                dropdown._values = [option.value for option in dropdown.options]

        # Update selected_ids
        self.selected_ids = []
        for dropdown, is_present in dropdowns:
            if is_present and dropdown.values:
                self.selected_ids.extend(dropdown.values)
        await interaction.response.edit_message(view=self)

    def create_deselect_all_button(self, row=4):
        button = discord.ui.Button(
            label="Deselect All",
            style=discord.ButtonStyle.secondary,
            row=row,
            custom_id="deselect_all_button"
        )
        button.callback = self.deselect_all_callback
        return button
    async def deselect_all_callback(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
            return

        dropdowns = [
            (self.selectable_creature_dropdown_1, len(self.creatures) > 0),
            (self.selectable_creature_dropdown_2, len(self.creatures) > 25),
            (self.selectable_creature_dropdown_3, len(self.creatures) > 50),
            (self.selectable_creature_dropdown_4, len(self.creatures) > 75)
        ]

        for dropdown, is_present in dropdowns:
            if is_present:
                dropdown._values = []

        self.selected_ids = []
        await interaction.response.edit_message(view=self)


    # CREATE DROPDOWNS
    def create_creature_dropdown(self, row=1, dropdown_num = 0):
        lower_bound = 0 + (dropdown_num * 25)
        upper_bound = min(25 + (dropdown_num * 25), len(self.creatures))

        options = [
            discord.SelectOption(
                label=f"{self.build_creature_dropdown_options(creature)}",
                value=creature.catch_id
            )
            for i, creature in enumerate(self.creatures[lower_bound: upper_bound])
        ]

        dropdown = Select(
            placeholder=f"Select creatures to {self.mode} ({lower_bound +1} - {upper_bound})",
            options=options,
            min_values=min(1, len(options)),
            max_values=len(options),
            row=row,
            custom_id=f"creature_dropdown_{dropdown_num}"
        )

        # Pre-select all options if select_all_enabled is True
        # if self.select_all_enabled and options:
        #     dropdown._values = [option.value for option in options]
        #     # Also update selected_ids with these values
        #     self.selected_ids.extend([option.value for option in options])

        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    async def avatar_dropdown_callback(self, interaction: discord.Interaction):
        self.selected_ids = []
        dropdowns = [
            self.selectable_creature_dropdown_1,
            self.selectable_creature_dropdown_2,
            self.selectable_creature_dropdown_3,
            self.selectable_creature_dropdown_4
        ]

        for dropdown in dropdowns:
            if dropdown.values:
                self.selected_ids.extend(dropdown.values)

        print(f"YOU HAVE SELECTED {self.selected_ids} CREATURES FOR {self.mode.upper()}.")

        await interaction.response.defer()


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self, view_state=None):
        self.view_state = view_state if view_state else self.view_state

        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        # UPDATE ENABLED/DISABLED STATES
        self.final_confirmation_button_yes.disabled = self.view_state != VIEW_WORKFLOW_STATE_CONFIRMATION
        self.final_confirmation_button_no.disabled = self.view_state != VIEW_WORKFLOW_STATE_CONFIRMATION
        self.confirmation_button.disabled = self.view_state != VIEW_WORKFLOW_STATE_INTERACTION
    def rebuild_view(self):
        for item in self.children.copy():
            self.remove_item(item)

        if self.view_state == VIEW_WORKFLOW_STATE_INTERACTION:
            self.add_item(self.confirmation_button)
            # self.add_item(self.select_all_button)
            # self.add_item(self.deselect_all_button)

            if len(self.creatures) > 0:
                self.add_item(self.selectable_creature_dropdown_1)
            if len(self.creatures) > 25:
                self.add_item(self.selectable_creature_dropdown_2)
            if len(self.creatures) > 50:
                self.add_item(self.selectable_creature_dropdown_3)
            if len(self.creatures) > 75:
                self.add_item(self.selectable_creature_dropdown_4)
        elif self.view_state == VIEW_WORKFLOW_STATE_CONFIRMATION:
            self.add_item(self.final_confirmation_button_yes)
            # self.add_item(self.final_confirmation_button_no)
        elif self.view_state == VIEW_WORKFLOW_STATE_FINALIZED:
            for item in self.children:
                item.disabled = True


    # SUPPORT FUNCTIONS
    def build_creature_dropdown_options(self, creature):
        creature_name = f'{creature.name}{f' -  {creature.variant_name}' if creature.variant_name != '' else ''}'
        nickname = f'{creature.nickname}' if creature.nickname != '' else creature.name

        creature_symbols =  '❗' if len(creature.nickname) > 0 else ''
        creature_symbols +=  '✨' if creature.local_rarity.name == TGOMMO_RARITY_MYTHICAL else ''

        return f"[{creature.catch_id}] \t ({pad_text(nickname, 20)}) \t {pad_text(creature_name, 20)}{creature_symbols}"

    def reload_creature_inventory_image(self, image_mode=None, creature_ids_to_update=None, refresh_creatures=False):
        new_image = self.creature_inventory_image_factory.get_creature_inventory_page_image(image_mode=image_mode, creature_ids_to_update=creature_ids_to_update, refresh_creatures=refresh_creatures, show_mythics_only=self.show_only_mythics, show_favorites_only=self.show_only_favorites, show_nicknames_only=self.show_only_nicknames)
        return convert_to_png(new_image, f'player_boxes_page.png')

    def reload_release_results_image(self, currency_earned=0, earned_items=None, count_released=0):
        new_image = self.release_result_image_factory.get_creature_inventory_page_image(currency=currency_earned, earned_items=earned_items, count_released=count_released)
        return convert_to_png(new_image, f'release_results.png')