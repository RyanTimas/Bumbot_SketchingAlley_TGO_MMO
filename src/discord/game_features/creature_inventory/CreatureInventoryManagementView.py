from discord.ui import Select

from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_user_db_handler, get_tgommo_db_handler
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous, jump
from src.resources.constants.TGO_MMO_constants import *



class CreatureInventoryManagementView(discord.ui.View):
    def __init__(self, message_author, mode, creatures, creature_inventory_image_factory: CreatureInventoryImageFactory, original_message=None, original_view=None, view_state= VIEW_WORKFLOW_STATE_INTERACTION):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.mode = mode

        self.creature_inventory_image_factory = creature_inventory_image_factory
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

                updated_image = self.reload_image(image_mode= self.mode, creature_ids_to_update= self.selected_ids)

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

                updated_image = self.reload_image(refresh_creatures=True, image_mode=final_image_mode, currency_earned=currency_earned if final_image_mode == CREATURE_INVENTORY_MODE_RELEASE_RESULTS else 0, earned_items=earned_items if final_image_mode == CREATURE_INVENTORY_MODE_RELEASE_RESULTS else None)
                self.refresh_view(view_state = VIEW_WORKFLOW_STATE_FINALIZED)
                await interaction.followup.send(content=f"You have successfully {self.mode}'d your guys", view=self, ephemeral=True)
                await self.original_message.edit(content="updated lol", attachments=[updated_image], view=self.original_view)

        return callback

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

    def reload_image(self, image_mode=None, creature_ids_to_update=None, refresh_creatures=False, currency_earned=0, earned_items=None):
        new_image = self.creature_inventory_image_factory.get_creature_inventory_page_image(image_mode=image_mode, creature_ids_to_update=creature_ids_to_update, refresh_creatures=refresh_creatures, currency=currency_earned, earned_items=earned_items)
        return convert_to_png(new_image, f'player_boxes_page.png')


    # REWARD ITEM HANDLING
    def handle_post_release_rewards(self):
        # add new currency to user profile based on number of released creatures
        currency_earned = self.calculate_new_currency_amount()

        earned_items = self.get_earned_items()

        return currency_earned,  earned_items

    def calculate_new_currency_amount(self):
        return random.randint(1, 5) * len(self.selected_ids)

    def get_earned_items(self):
        earned_items = []
        earned_items.append(self.rewardable_items[0])
        earned_items.append(self.rewardable_items[0])
        earned_items.append(self.rewardable_items[1])
        earned_items.append(self.rewardable_items[1])
        earned_items.append(self.rewardable_items[1])
        earned_items.append(self.rewardable_items[2])

        # for each released creature, roll for item based on predefined drop rates
        for selected_id in self.selected_ids:
            # roll for random item
            earned_items.extend(self.get_random_items(creature= get_tgommo_db_handler().get_creature_by_catch_id(selected_id), iteration=1))

            # todo: roll for release amount bonus items

            # todo: roll for default items

        # Convert to list of tuples (item, count)
        item_counts = {}
        for item in earned_items:
            if item in item_counts:
                item_counts[item] += 1
            else:
                item_counts[item] = 1

        return [(item, count) for item, count in item_counts.items()]

    def get_random_items(self, creature, iteration=1, random_items = []):

        if random.randint(1, 25) <= 10:
            earned_item = self.roll_for_random_item(get_tgommo_db_handler().get_creature_by_catch_id(creature))
            random_items.append(earned_item)

        return random_items if len(random_items) < iteration else self.get_random_items(creature, iteration +1, random_items)

    def roll_for_random_item(self, creature):
        reward_pool = []

        for item in self.rewardable_items:
            if item.item_type == ITEM_TYPE_BAIT:
                rate = 1

                # perform rarity matching bonus
                if creature.rarity.name == item.rarity.name:
                    rate = rate * 10

                reward_pool.extend([item.item_id] * rate)

        return reward_pool[random.randint(0, len(reward_pool) -1)]