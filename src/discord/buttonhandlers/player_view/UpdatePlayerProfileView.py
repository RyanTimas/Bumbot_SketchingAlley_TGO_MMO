import discord
from discord.ui import Modal, TextInput, Button, Select

from src.commons.CommonFunctions import retry_on_ssl_error, pad_text
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

        self.creature_id_1 = player.creature_slot_id_1 if player.creature_slot_id_1 != -1 else ''
        self.creature_id_2 = player.creature_slot_id_2 if player.creature_slot_id_2 != -1 else ''
        self.creature_id_3 = player.creature_slot_id_3 if player.creature_slot_id_3 != -1 else ''
        self.creature_id_4 = player.creature_slot_id_4 if player.creature_slot_id_4 != -1 else ''
        self.creature_id_5 = player.creature_slot_id_5 if player.creature_slot_id_5 != -1 else ''
        self.creature_id_6 = player.creature_slot_id_6 if player.creature_slot_id_6 != -1 else ''

        self.user_creature_collection = get_tgommo_db_handler().get_creature_collection_by_user(self.user_id)

        self.currency = player.currency
        self.available_catches = player.available_catches
        self.rod_level = player.rod_level
        self.rod_amount = player.rod_amount
        self.trap_level = player.trap_level
        self.trap_amount = player.trap_amount

        # LOAD VIEW COMPONENTS
        # buttons
        update_profile_button_1 = self.create_update_profile_button(page=1, row=2)
        update_profile_button_2 = self.create_update_profile_button(page=2,row=2)
        display_creatures_button = self.display_creature_collection_button(row=3)
        save_changes_button = self.create_save_changes_button(row=4)

        # text inputs
        self.display_name_input = TextInput(label="Display Name (12 chars max)", default=f"{self.display_name}", placeholder="Set your display name", max_length=20, required=False)
        self.display_creature_1_input = TextInput(label="Display Creature 1", default=f"{self.creature_id_1}", placeholder="Set creature ID for slot 1 (use 'See Creature Storage' to view options)", max_length=5, required=False)
        self.display_creature_2_input = TextInput(label="Display Creature 2", default=f"{self.creature_id_2}" if player.creature_slot_id_6 != -1 else '', placeholder="Set creature ID for slot 2", max_length=5, required=False)
        self.display_creature_3_input = TextInput(label="Display Creature 3", default=f"{self.creature_id_3}", placeholder="Set creature ID for slot 3 (use 'See Creature Storage' to view options)", max_length=5, required=False)
        self.display_creature_4_input = TextInput(label="Display Creature 4", default=f"{self.creature_id_4}", placeholder="Set creature ID for slot 4 (use 'See Creature Storage' to view options)", max_length=5, required=False)
        self.display_creature_5_input = TextInput(label="Display Creature 5", default=f"{self.creature_id_5}", placeholder="Set creature ID for slot 5 (use 'See Creature Storage' to view options)", max_length=5, required=False)
        self.display_creature_6_input = TextInput(label="Display Creature 6", default=f"{self.creature_id_6}", placeholder="Set creature ID for slot 6 (use 'See Creature Storage' to view options)", max_length=5, required=False)

        self.remove_display_creature_input = TextInput(label="Index of Creature to Remove", default=f"", placeholder="Which creature Slot would you like to remove? (1-6)", max_length=1, required=False)

        self.modal_lock = False

        # dropdowns
        avatar_picker_dropdown = self.create_avatar_picker_dropdown(row=1)
        background_picker_dropdown = self.create_background_picker_dropdown(row=2)


        # ADD COMPONENTS TO VIEW
        self.add_item(avatar_picker_dropdown)                 # row 1
        # self.add_item(background_picker_dropdown)        # row 2

        self.add_item(update_profile_button_1)                    # row 3
        self.add_item(update_profile_button_2)                    # row 3
        self.add_item(display_creatures_button)               # row 3

        self.add_item(save_changes_button)                    # row 4


    # CREATE BUTTONS
    def create_update_profile_button(self, page, row=0):
        button = Button(label=f"Change Profile - {page}", style=discord.ButtonStyle.blurple, row=row)
        button.callback = self.update_profile_button_callback_page_1 if page == 1 else self.update_profile_button_callback_page_2
        return button
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def update_profile_button_callback_page_1(self, interaction: discord.Interaction):
        self.update_modal_text_inputs()
        await interaction.response.send_modal(self.create_user_details_modal(options=(self.display_name_input, self.display_creature_1_input, self.display_creature_2_input, self.display_creature_3_input)))

    @retry_on_ssl_error(max_retries=3, delay=1)
    async def update_profile_button_callback_page_2(self, interaction: discord.Interaction):
        self.update_modal_text_inputs()
        await interaction.response.send_modal(self.create_user_details_modal(options=(self.display_creature_4_input, self.display_creature_5_input, self.display_creature_6_input)))

    def create_save_changes_button(self, row=0):
        button = Button(label="Save Changes", style=discord.ButtonStyle.green, row=row)
        button.callback = self.save_changes_button_callback
        return button
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def save_changes_button_callback(self, interaction: discord.Interaction):
        # filter creature IDs to ensure they are valid
        await self.handle_invalid_creature_ids(interaction)

        params = (self.display_name,self.avatar_id,self.background_id,self.creature_id_1,self.creature_id_2,self.creature_id_3,self.creature_id_4,self.creature_id_5,self.creature_id_6, self.currency,self.available_catches, self.rod_level, self.rod_amount,self.trap_level,self.trap_amount, self.user_id)
        get_tgommo_db_handler().update_user_profile(params=params)

        await interaction.response.send_message("Changes successfully saved!", ephemeral=True)

    def display_creature_collection_button(self, row=0):
        button = Button(label="See Creature Storage", style=discord.ButtonStyle.red, row=row)
        button.callback = self.display_creature_collection_callback
        return button
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def display_creature_collection_callback(self, interaction: discord.Interaction):
        await self.build_user_creature_collection(interaction)


    # CREATE MODALS
    def create_user_details_modal(self, options):
        user_details_modal = Modal(title="Update Profile Details")

        for option in options:
            user_details_modal.add_item(option)

        user_details_modal.on_submit = self.user_details_modal_on_submit
        return user_details_modal
    async def user_details_modal_on_submit(self, interaction: discord.Interaction):
        self.display_name = self.display_name_input.value if self.display_name_input.value != '' else self.display_name
        self.creature_id_1 = self.display_creature_1_input.value
        self.creature_id_2 = self.display_creature_2_input.value
        self.creature_id_3 = self.display_creature_3_input.value
        self.creature_id_4 = self.display_creature_4_input.value
        self.creature_id_5 = self.display_creature_5_input.value
        self.creature_id_6 = self.display_creature_6_input.value

        await interaction.response.send_message(f"Successfully modified player info - Remember to save your changes!", ephemeral=True)


    # CREATE DROPDOWNS
    def create_avatar_picker_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Avatar {i}", value=str(i)) for i in range(1, 3)]
        dropdown = Select(placeholder="Choose Avatar", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    async def avatar_dropdown_callback(self, interaction: discord.Interaction):
        # Access the selected value from the interaction
        self.avatar_id = int(interaction.data["values"][0])
        await interaction.response.defer()

    def create_background_picker_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Background {i}", value=str(i)) for i in range(1, 2)]
        dropdown = Select(placeholder="Choose Background Style", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    async def background_dropdown_callback(self, interaction: discord.Interaction):
        # Access the selected value from the interaction
        self.background_id = int(interaction.data["values"][0])


    # SUPPORT FUNCTIONS
    async def build_user_creature_collection(self, interaction: discord.Interaction):
        page_num = 0
        pages = [f"Total Unique Creatures Caught: {len(self.user_creature_collection)}"]

        # add an entry for each creature in collection
        for creature_index, creature in enumerate(self.user_creature_collection):
            current_page = pages[page_num]

            catch_id = creature[0]
            creature_id = creature[1]
            creature_name = f'{creature[2]}{f' -  {creature[3]}' if creature[3] != '' else ''}'
            spawn_rarity = creature[5]
            is_mythical = creature[6]
            nickname = f'**__{creature[4]}❗__**' if creature[4] != '' else creature[2] + ('✨' if is_mythical else '')

            newlines = f'{'\n' if creature_id != self.user_creature_collection[creature_index - 1][1] else ''}\n'
            new_entry = f"{newlines}{creature_index + 1}.  \t\t [{catch_id}] \t ({pad_text(creature_name, 20)}) \t {pad_text(nickname, 20)}"

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
                if str(creature[0]) == str(display_creature_id):
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


    def update_modal_text_inputs(self):
        self.display_name_input = TextInput(label="DisplayName", default=f"{self.display_name}", placeholder="Set your display name", max_length=20, required=False)

        self.display_creature_1_input = TextInput(label="Display Creature 1", default=f"{self.creature_id_1}",placeholder="Set creature ID for slot 1 (use 'See Creature Storage' to view options)",max_length=20, required=False)
        self.display_creature_2_input = TextInput(label="Display Creature 2", default=f"{self.creature_id_2}",placeholder="Set creature ID for slot 2 (use 'See Creature Storage' to view options)",max_length=20, required=False)
        self.display_creature_3_input = TextInput(label="Display Creature 3", default=f"{self.creature_id_3}",placeholder="Set creature ID for slot 3 (use 'See Creature Storage' to view options)", max_length=20, required=False)
        self.display_creature_4_input = TextInput(label="Display Creature 4", default=f"{self.creature_id_4}",placeholder="Set creature ID for slot 4 (use 'See Creature Storage' to view options)",max_length=20, required=False)
        self.display_creature_5_input = TextInput(label="Display Creature 5", default=f"{self.creature_id_5}",placeholder="Set creature ID for slot 5 (use 'See Creature Storage' to view options)",max_length=20, required=False)
        self.display_creature_6_input = TextInput(label="Display Creature 6", default=f"{self.creature_id_6}",placeholder="Set creature ID for slot 6 (use 'See Creature Storage' to view options)",max_length=20, required=False)