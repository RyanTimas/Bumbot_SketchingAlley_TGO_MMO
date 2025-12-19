import asyncio

import discord
from discord.ui import Modal, TextInput, Button, Select

from src.commons.CommonFunctions import retry_on_ssl_error, pad_text, convert_to_png, \
    create_dummy_label_button, check_if_user_can_interact_with_view, create_close_button
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous
from src.discord.general.handlers.AvatarUnlockHandler import AvatarUnlockHandler
from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.TGO_MMO_constants import TGOMMO_RARITY_MYTHICAL


class UpdatePlayerProfileView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, user_id: int, player: TGOPlayer, player_profile_image_factory=None, original_view=None, original_message=None):
        super().__init__(timeout=None)

        # LOAD VARIABLES
        self.player = player

        self.user_id = user_id
        self.interaction = interaction

        self.display_name = player.nickname

        self.current_avatar_id = player.avatar.avatar_id
        self.unlocked_avatars = get_tgommo_db_handler().get_unlocked_avatars_by_user_id(self.user_id, convert_to_object=True)
        self.unlocked_avatars = self.unlocked_avatars

        self.avatar_page_capacity = 25
        self.avatar_dropdown_page_num = 1
        self.avatar_dropdown_total_pages = ((len(self.unlocked_avatars) - 1) // self.avatar_page_capacity) + 1

        self.background_id = player.background_id

        self.creature_id_1 = player.creature_slot_id_1 if player.creature_slot_id_1 != -1 else ''
        self.creature_id_2 = player.creature_slot_id_2 if player.creature_slot_id_2 != -1 else ''
        self.creature_id_3 = player.creature_slot_id_3 if player.creature_slot_id_3 != -1 else ''
        self.creature_id_4 = player.creature_slot_id_4 if player.creature_slot_id_4 != -1 else ''
        self.creature_id_5 = player.creature_slot_id_5 if player.creature_slot_id_5 != -1 else ''
        self.creature_id_6 = player.creature_slot_id_6 if player.creature_slot_id_6 != -1 else ''

        self.user_creature_collection = get_tgommo_db_handler().get_user_creatures_by_user_id(self.user_id, convert_to_object=True, )

        self.player_profile_image_factory = player_profile_image_factory
        self.original_view = original_view
        self.original_message = original_message

        self.currency = player.currency
        self.available_catches = player.available_catches
        self.rod_level = player.rod_level
        self.rod_amount = player.rod_amount
        self.trap_level = player.trap_level
        self.trap_amount = player.trap_amount

        self.interaction_lock = asyncio.Lock()

        # LOAD VIEW COMPONENTS
        # buttons
        update_profile_button_1 = self.create_update_profile_button(page=1, row=2)
        update_profile_button_2 = self.create_update_profile_button(page=2,row=2)
        display_creatures_button = self.display_creature_collection_button(row=3)
        save_changes_button = self.create_save_changes_button(row=4)
        close_button = create_close_button(row=4, interaction_lock=self.interaction_lock, message_author_id=self.user_id)

        self.next_avatars_button = self.create_avatar_dropdown_navigation_button(is_next=True, row=0)
        self.previous_avatars_button = self.create_avatar_dropdown_navigation_button(is_next=False, row=0)
        self.placeholder_avatar_options_button = create_dummy_label_button(label_text=f"-----Avatars-----", row=0)

        # text inputs
        self.display_name_input = TextInput(label="Display Name (12 chars max)", default=f"{self.display_name}", placeholder="Set your display name", max_length=20, required=False)
        self.display_creature_1_input = None
        self.display_creature_2_input = None
        self.display_creature_3_input = None
        self.display_creature_4_input = None
        self.display_creature_5_input = None
        self.display_creature_6_input = None

        self.remove_display_creature_input = TextInput(label="Index of Creature to Remove", default=f"", placeholder="Which creature Slot would you like to remove? (1-6)", max_length=1, required=False)

        self.modal_lock = False

        # dropdowns
        self.avatar_picker_dropdown = self.create_avatar_picker_dropdown(row=1)
        background_picker_dropdown = self.create_background_picker_dropdown(row=2)

        # ADD COMPONENTS TO VIEW
        # row 1
        if len(self.unlocked_avatars) > self.avatar_page_capacity:
            self.add_item(self.previous_avatars_button)
            self.add_item(self.placeholder_avatar_options_button)
            self.add_item(self.next_avatars_button)
        # row 2
        self.add_item(self.avatar_picker_dropdown)
        # row 3
        self.add_item(create_dummy_label_button(label_text="Update Profile:", row=2))
        self.add_item(update_profile_button_1)
        self.add_item(update_profile_button_2)
        # row 4
        self.add_item(display_creatures_button)
        # row 5
        self.add_item(save_changes_button)
        self.add_item(close_button)

        self.update_view_components()

    # CREATE BUTTONS
    def create_avatar_dropdown_navigation_button(self, is_next, row=0):
        button = Button(
            label="➡️" if is_next else "⬅️",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=next_ if is_next else previous)
        return button
    def nav_callback(self, new_page,):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.player.user_id):
                return

            await interaction.response.defer()

            self.avatar_dropdown_page_num += 1 if new_page == next_ else -1
            self.update_view_components()

            await interaction.message.edit(view=self)
        return callback

    def create_update_profile_button(self, page, row=0):
        button = Button(label=f"Change Profile - {page}", style=discord.ButtonStyle.blurple, row=row)
        button.callback = self.update_profile_button_callback_page_1 if page == 1 else self.update_profile_button_callback_page_2
        return button
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def update_profile_button_callback_page_1(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.player.user_id):
            return

        self.update_view_components()
        await interaction.response.send_modal(self.create_user_details_modal(options=(self.display_name_input, self.display_creature_1_input, self.display_creature_2_input, self.display_creature_3_input)))
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def update_profile_button_callback_page_2(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.player.user_id):
            return

        self.update_view_components()
        await interaction.response.send_modal(self.create_user_details_modal(options=(self.display_creature_4_input, self.display_creature_5_input, self.display_creature_6_input)))

    def create_save_changes_button(self, row=0):
        button = Button(label="Save Changes", style=discord.ButtonStyle.green, row=row)
        button.callback = self.save_changes_button_callback
        return button
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def save_changes_button_callback(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.player.user_id):
            return

        # filter creature IDs to ensure they are valid
        await self.handle_invalid_creature_ids(interaction)

        creature_slot_1 = int(self.creature_id_1) if self.creature_id_1 != '' else -1
        creature_slot_2 = int(self.creature_id_2) if self.creature_id_2 != '' else -1
        creature_slot_3 = int(self.creature_id_3) if self.creature_id_3 != '' else -1
        creature_slot_4 = int(self.creature_id_4) if self.creature_id_4  != '' else -1
        creature_slot_5 = int(self.creature_id_5) if self.creature_id_5 != '' else -1
        creature_slot_6 = int(self.creature_id_6) if self.creature_id_6 != '' else -1

        params = (self.display_name, self.current_avatar_id, self.background_id,  creature_slot_1, creature_slot_2, creature_slot_3, creature_slot_4, creature_slot_5, creature_slot_6, self.currency, self.available_catches, self.rod_level, self.rod_amount, self.trap_level, self.trap_amount, self.user_id)
        get_tgommo_db_handler().update_user_profile(params=params)

        self.player_profile_image_factory.load_player_info()
        new_image = self.player_profile_image_factory.build_player_profile_page_image(tab_is_open=False)
        new_png = convert_to_png(new_image, f'player_profile_page.png')

        await self.original_message.edit(attachments=[new_png], view=self.original_view)

        await interaction.response.send_message("Changes successfully saved!", ephemeral=True)
        await AvatarUnlockHandler(user_id=interaction.user.id, nickname=self.display_name, interaction=interaction).check_avatar_unlock_conditions()
        await interaction.message.delete(delay=2)

    def display_creature_collection_button(self, row=0):
        button = Button(label="See Creature Storage", style=discord.ButtonStyle.red, row=row)
        button.callback = self.display_creature_collection_callback
        return button
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def display_creature_collection_callback(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.user_id):
            return
        await self.build_user_creature_collection(interaction)


    # CREATE MODALS
    def create_user_details_modal(self, options):
        user_details_modal = Modal(title="Update Profile Details")

        for option in options:
            user_details_modal.add_item(option)

        user_details_modal.on_submit = self.user_details_modal_on_submit
        return user_details_modal
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def user_details_modal_on_submit(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.player.user_id):
            return

        self.display_name = self.display_name_input.value if self.display_name_input.value != '' else self.display_name
        self.creature_id_1 = self.display_creature_1_input.value if self.display_creature_1_input.value != '' else -1
        self.creature_id_2 = self.display_creature_2_input.value if self.display_creature_2_input.value != '' else -1
        self.creature_id_3 = self.display_creature_3_input.value if self.display_creature_3_input.value != '' else -1
        self.creature_id_4 = self.display_creature_4_input.value if self.display_creature_4_input.value != '' else -1
        self.creature_id_5 = self.display_creature_5_input.value if self.display_creature_5_input.value != '' else -1
        self.creature_id_6 = self.display_creature_6_input.value if self.display_creature_6_input.value != '' else -1

        await interaction.response.send_message(f"Successfully modified player info - Remember to save your changes!", ephemeral=True)


    # CREATE DROPDOWNS
    def create_avatar_picker_dropdown(self, row=1):
        dropdown = Select(placeholder="Choose Avatar", options=self.get_avatar_dropdown_options(), min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def avatar_dropdown_callback(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.player.user_id):
            return

        # Access the selected value from the interaction
        self.current_avatar_id = interaction.data["values"][0]
        await interaction.response.defer()

    def create_background_picker_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Background {i}", value=str(i)) for i in range(1, 2)]
        dropdown = Select(placeholder="Choose Background Style", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def background_dropdown_callback(self, interaction: discord.Interaction):
        # Access the selected value from the interaction
        self.background_id = int(interaction.data["values"][0])


    # SUPPORT FUNCTIONS
    async def build_user_creature_collection(self, interaction: discord.Interaction):
        page_num = 0
        pages = [f"Total Unique Creatures Caught: {len(self.user_creature_collection)}"]

        ordered_creatures = sorted(self.user_creature_collection, key=lambda c: c.dex_no)

        # add an entry for each creature in collection
        for creature_index, creature in enumerate(ordered_creatures):
            current_page = pages[page_num]

            creature_name = f'{creature.name}{f' -  {creature.variant_name}' if creature.variant_name != '' else ''}'
            nickname = f'**__{creature.nickname}❗__**' if creature.nickname != '' else creature.name + ('✨' if creature.rarity.name == TGOMMO_RARITY_MYTHICAL else '')

            newlines = f'{'\n' if creature.catch_id != ordered_creatures[creature_index - 1].catch_id else ''}\n'
            new_entry = f"{newlines}{creature_index + 1}.  \t\t [{creature.catch_id}] \t ({pad_text(creature_name, 20)}) \t {pad_text(nickname, 20)}"

            if len(current_page) + len(new_entry) > 1900:
                page_num += 1
                pages.append('')

            pages[page_num] += new_entry

        # Send the first page as the response
        text = f"\n# {self.display_name}'s Creature Collection (1/{len(pages)}):\n{pages[0]}"
        await interaction.response.send_message(text, ephemeral=True)

        # create page images for user to see
        for page_index, page in enumerate(pages):
            if page_index == 0:
                continue

            text = f"\n# {self.display_name}'s Creature Collection ({page_index + 1}/{len(pages)}):\n{page}"
            await interaction.followup.send(text, ephemeral=True)


    async def handle_invalid_creature_ids(self, interaction: discord.Interaction):
        warnings = ["_⚠️**WARNING:**⚠️_\n"]

        # check for non-integer or negative creature IDs
        has_invalid_ids, invalid_slots = self.check_for_invalid_creature_ids()
        if has_invalid_ids:
            invalid_positions = ', '.join(str(pos[1]) for pos in invalid_slots)
            warnings.append(f"* Invalid creature IDs found at positions:\t{invalid_positions}")

            # await interaction.response.send_message(f"⚠️WARNING: \n Invalid creature IDs found at positions: \n> {invalid_positions}.\n These positions were reset to empty.",ephemeral=True)
            self.reset_display_creature_ids(invalid_slots)

        # check if any duplicate IDs were input
        has_duplicates, duplicates = self.check_for_duplicate_creature_ids()

        if has_duplicates:
            print('yep duplicates')
            duplicate_positions = ', '.join(str(pos[1]) for pos in duplicates)
            warnings.append(f"* Duplicate creature IDs found at positions:\t{duplicate_positions}")

            # await interaction.response.send_message(f"⚠️WARNING: \n There were duplicate creatures found at positions: \n> {duplicate_positions}.\n These positions were not set.",ephemeral=True)
            self.reset_display_creature_ids(duplicates)

        # check user owns all creatures in display slots
        has_unowned_creatures, violations = self.check_creature_id_in_collection()
        if has_unowned_creatures:
            print('yep unowned')
            violation_positions = ', '.join(str(pos[1]) for pos in violations)
            warnings.append(f"* You do not own the creatures in the following display positions:\t{violation_positions}")

            # await interaction.response.send_message(f"⚠️WARNING: \n You do not own the creatures in the following display positions: \n> {violation_positions}.\n These positions were not set.", ephemeral=True)
            self.reset_display_creature_ids(violations)

        if len(warnings) > 1:
            warnings.append("\n These positions were reset to empty.")

            warning_message = '\n'.join(warnings)
            await interaction.response.send_message(warning_message, ephemeral=True)

    def check_for_duplicate_creature_ids(self):
        # Create list of creature IDs with their positions
        violated_indexes = []
        seen_ids = []

        display_creature_ids = [(self.creature_id_1, 1), (self.creature_id_2, 2), (self.creature_id_3, 3), (self.creature_id_4, 4), (self.creature_id_5, 5), (self.creature_id_6, 6)]

        for creature_id, pos in display_creature_ids:
            if not creature_id or str(creature_id) == "-1":
                continue

            if creature_id in seen_ids:
                violated_indexes.append((creature_id, pos))
            else:
                seen_ids.append(creature_id)

        return len(violated_indexes) != 0,  violated_indexes

    def check_creature_id_in_collection(self):
        violated_indexes = []

        display_creature_ids = [(self.creature_id_1, 1), (self.creature_id_2, 2), (self.creature_id_3, 3), (self.creature_id_4, 4), (self.creature_id_5, 5), (self.creature_id_6, 6)]

        for display_creature_id, display_creature_index in display_creature_ids:
            if not display_creature_id or str(display_creature_id) == "-1":
                continue

            found_in_collection = False

            for creature in self.user_creature_collection:
                if str(creature.catch_id) == str(display_creature_id):
                    found_in_collection = True
                    break

            if not found_in_collection:
                violated_indexes.append((display_creature_id, display_creature_index))

        return len(violated_indexes) != 0, violated_indexes

    def check_for_invalid_creature_ids(self):
        invalid_slots = []

        display_creature_ids = [(self.creature_id_1, 1), (self.creature_id_2, 2), (self.creature_id_3, 3),
                                (self.creature_id_4, 4), (self.creature_id_5, 5), (self.creature_id_6, 6)]

        for creature_id, pos in display_creature_ids:
            # Skip empty slots
            if not creature_id or str(creature_id) == "-1":
                continue

            try:
                # Check if it's a valid positive integer
                id_as_int = int(creature_id)
                if id_as_int <= 0:
                    invalid_slots.append((creature_id, pos))
            except ValueError:
                # Not a valid integer
                invalid_slots.append((creature_id, pos))

        return len(invalid_slots) > 0, invalid_slots

    def reset_display_creature_ids(self, positions):
        # Create attribute mapping for easier setting
        creature_id_attrs = {1: 'creature_id_1', 2: 'creature_id_2', 3: 'creature_id_3', 4: 'creature_id_4', 5: 'creature_id_5', 6: 'creature_id_6'}

        # For each duplicate ID, clear all but the first occurrence
        for duplicate_id, position in positions:
            setattr(self, creature_id_attrs[position], "-1")

    def get_avatar_dropdown_options(self):
        first_index = ((self.avatar_dropdown_page_num - 1) * self.avatar_page_capacity)
        last_index = min(self.avatar_dropdown_page_num * self.avatar_page_capacity, len(self.unlocked_avatars))

        return [discord.SelectOption(label=f"Avatar {i+1} - {self.unlocked_avatars[i].name}", value=str(self.unlocked_avatars[i].avatar_id)) for i in range(first_index, last_index)]

    # BUILD VIEW CONTENT
    def update_view_components(self):
        self.update_modal_text_inputs()
        self.update_button_states()
        self.update_dropdown_options()

    def update_modal_text_inputs(self):
        self.display_name_input = TextInput(label="DisplayName", default=f"{self.display_name}", placeholder="Set your display name", max_length=20, required=False)

        self.display_creature_1_input = TextInput(label="Display Creature 1", default=f"{self.creature_id_1 if self.creature_id_1 != -1 else ''}",placeholder="Set creature ID for slot 1 (use 'See Creature Storage' to view options)",max_length=20, required=False)
        self.display_creature_2_input = TextInput(label="Display Creature 2", default=f"{self.creature_id_2 if self.creature_id_2 != -1 else ''}",placeholder="Set creature ID for slot 2 (use 'See Creature Storage' to view options)",max_length=20, required=False)
        self.display_creature_3_input = TextInput(label="Display Creature 3", default=f"{self.creature_id_3 if self.creature_id_3 != -1 else ''}",placeholder="Set creature ID for slot 3 (use 'See Creature Storage' to view options)", max_length=20, required=False)
        self.display_creature_4_input = TextInput(label="Display Creature 4", default=f"{self.creature_id_4 if self.creature_id_4 != -1 else ''}",placeholder="Set creature ID for slot 4 (use 'See Creature Storage' to view options)",max_length=20, required=False)
        self.display_creature_5_input = TextInput(label="Display Creature 5", default=f"{self.creature_id_5 if self.creature_id_5 != -1 else ''}",placeholder="Set creature ID for slot 5 (use 'See Creature Storage' to view options)",max_length=20, required=False)
        self.display_creature_6_input = TextInput(label="Display Creature 6", default=f"{self.creature_id_6 if self.creature_id_6 != -1 else ''}",placeholder="Set creature ID for slot 6 (use 'See Creature Storage' to view options)",max_length=20, required=False)

    def update_dropdown_options(self):
        self.avatar_picker_dropdown.options = self.get_avatar_dropdown_options()

    def update_button_states(self):
        first_index = ((self.avatar_dropdown_page_num - 1) * self.avatar_page_capacity) + 1
        last_index = min(self.avatar_dropdown_page_num * self.avatar_page_capacity, len(self.unlocked_avatars))
        self.placeholder_avatar_options_button.label = f"-----Avatars ({first_index} - {last_index})-----"

        self.next_avatars_button.disabled = self.avatar_dropdown_page_num >= self.avatar_dropdown_total_pages
        self.previous_avatars_button.disabled = self.avatar_dropdown_page_num == 1
