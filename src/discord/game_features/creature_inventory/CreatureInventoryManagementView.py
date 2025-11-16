from discord.ui import Select

from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.creature_inventory.ReleaseResultImageFactory import ReleaseResultImageFactory
from src.discord.objects.CreatureRarity import get_rarity_hierarchy_value
from src.resources.constants.TGO_MMO_constants import *


class CreatureInventoryManagementView(discord.ui.View):
    def __init__(self, message_author, mode, creatures, creature_inventory_image_factory: CreatureInventoryImageFactory, original_message=None, original_view=None, view_state= VIEW_WORKFLOW_STATE_INTERACTION):
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

        self.rewardable_items = get_tgommo_db_handler().get_items_for_release(convert_to_object=True)

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
    def final_confirmation_callback(self, is_confirm=True):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                perform_operation = {
                    CREATURE_INVENTORY_MODE_RELEASE: lambda: get_tgommo_db_handler().update_user_creature_set_is_released(creature_ids=self.selected_ids),
                    CREATURE_INVENTORY_MODE_FAVORITE: lambda: get_tgommo_db_handler().update_user_creature_set_is_favorite(creature_ids=self.selected_ids)
                }

                if not perform_operation[self.mode]():
                    await interaction.followup.send(content=f"An error occurred while trying to {self.mode} your creatures. Please try again.", ephemeral=True)
                    return

                # if user chose to release creatures, give rewards
                final_image_mode = CREATURE_INVENTORY_MODE_DEFAULT
                if self.mode == CREATURE_INVENTORY_MODE_RELEASE:
                    currency_earned, earned_items = self.handle_post_release_rewards()

                    get_tgommo_db_handler().update_user_profile_currency(user_id=self.message_author.id, new_currency=currency_earned)
                    # get_tgommo_db_handler().add_items_to_user_profile(user_id=self.message_author.id, items=earned_items)

                    final_image_mode = CREATURE_INVENTORY_MODE_RELEASE_RESULTS

                self.refresh_view(view_state = VIEW_WORKFLOW_STATE_FINALIZED)

                # SEND MESSAGES
                await interaction.followup.send(content=f"You have successfully {self.mode}'d your guys", view=self, ephemeral=True)

                # always update original message to reflect changes
                updated_creature_inventory_image = self.reload_creature_inventory_image(refresh_creatures=True, image_mode=CREATURE_INVENTORY_MODE_DEFAULT, )
                await self.original_message.edit(content="updated lol", attachments=[updated_creature_inventory_image], view=self.original_view)

                # if releasing, show results image
                if final_image_mode == CREATURE_INVENTORY_MODE_RELEASE_RESULTS:
                    release_results_image = self.reload_release_results_image(currency_earned=currency_earned, earned_items=earned_items, count_released=len(self.selected_ids))
                    await interaction.channel.send(files=[release_results_image])
        return callback

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
                dropdown.values_ = []

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
            custom_id=f"creature_dropdown_{dropdown_num}",
        )

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
                self.remove_item(item)


    # SUPPORT FUNCTIONS
    def build_creature_dropdown_options(self, creature):
        creature_name = f'{creature.name}{f' -  {creature.variant_name}' if creature.variant_name != '' else ''}'
        nickname = f'{creature.nickname}' if creature.nickname != '' else creature.name

        creature_symbols =  '❗' if len(creature.nickname) > 0 else ''
        creature_symbols +=  '✨' if creature.rarity.name == TGOMMO_RARITY_MYTHICAL else ''

        return f"[{creature.catch_id}] \t ({pad_text(nickname, 20)}) \t {pad_text(creature_name, 20)}{creature_symbols}"

    def reload_creature_inventory_image(self, image_mode=None, creature_ids_to_update=None, refresh_creatures=False):
        new_image = self.creature_inventory_image_factory.get_creature_inventory_page_image(image_mode=image_mode, creature_ids_to_update=creature_ids_to_update, refresh_creatures=refresh_creatures)
        return convert_to_png(new_image, f'player_boxes_page.png')

    def reload_release_results_image(self, currency_earned=0, earned_items=None, count_released=0):
        new_image = self.release_result_image_factory.get_creature_inventory_page_image(currency=currency_earned, earned_items=earned_items, count_released=count_released)
        return convert_to_png(new_image, f'release_results.png')


# TODO: MOVE TO SEPARATE FILE
    # REWARD ITEM HANDLING
    def handle_post_release_rewards(self):
        currency_earned = self.calculate_new_currency_amount()
        earned_items = self.get_earned_items()
        return currency_earned,  earned_items

    def calculate_new_currency_amount(self):
        total_currency = 0
        for _ in self.selected_ids:
            total_currency += random.randint(1, 5)
        return total_currency

    def get_earned_items(self):
        earned_items = []

        # for each released creature, roll for item based on predefined drop rates
        for selected_id in self.selected_ids:
            creature = get_tgommo_db_handler().get_creature_by_catch_id(selected_id, convert_to_object=True)

            # roll for random item
            earned_items.extend(self.get_random_items(creature= creature))

            # todo: roll for release amount bonus items

            # todo: roll for default items

        # Convert to list of tuples (item, count)
        return self.convert_items_to_count_map(earned_items)


    def get_random_items(self, creature):
        rarity_item_drop_rates = {
            TGOMMO_RARITY_COMMON: 15,
            TGOMMO_RARITY_UNCOMMON: 25,
            TGOMMO_RARITY_NORMAL: 25,
            TGOMMO_RARITY_RARE: 10,
            TGOMMO_RARITY_EPIC: 10,
            TGOMMO_RARITY_LEGENDARY: 5,
            TGOMMO_RARITY_MYTHICAL: 5,
            TGOMMO_RARITY_TRANSCENDANT: 10,
            TGOMMO_RARITY_OMNIPOTENT: 1
        }

        if random.randint(1, rarity_item_drop_rates[creature.rarity.name]) == 1:
            earned_item = self.roll_for_random_item(creature)
            return [earned_item,]
        return []

    def roll_for_random_item(self, creature):
        reward_pool = []
        creature_rarity_hierarchy_value = get_rarity_hierarchy_value(creature.rarity.name)

        rarity_bonuses_rates = {
            TGOMMO_RARITY_COMMON: 25,
            TGOMMO_RARITY_UNCOMMON: 25,
            TGOMMO_RARITY_NORMAL: 15,
            TGOMMO_RARITY_EPIC: 10,
            TGOMMO_RARITY_RARE: 10,
            TGOMMO_RARITY_LEGENDARY: 7,
            TGOMMO_RARITY_MYTHICAL: 5,
            TGOMMO_RARITY_TRANSCENDANT: 1,
            TGOMMO_RARITY_OMNIPOTENT: 1
        }

        for item in self.rewardable_items:
            # only throw items at or above the creature's rarity into the pool
            if item.item_type == ITEM_TYPE_BAIT:
                item_rarity_level = get_rarity_hierarchy_value(item.rarity.name)

                if item_rarity_level >= creature_rarity_hierarchy_value:
                    rate = 1 * rarity_bonuses_rates[item.rarity.name]

                    # perform rarity matching bonus
                    if creature.rarity.name == item.rarity.name:
                        rate = 50

                    reward_pool.extend([item] * rate)
        return reward_pool[random.randint(0, len(reward_pool) -1)]

    def convert_items_to_count_map(self, earned_items):
        # Convert to list of tuples (item, count)
        item_counts = {}
        for item in earned_items:
            item_counts[item] = (item_counts[item] + 1) if item in item_counts else 1
        return [(item, count) for item, count in item_counts.items()]

