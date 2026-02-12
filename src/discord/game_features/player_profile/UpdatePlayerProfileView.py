import discord
from discord.ui import Modal, TextInput, Button, Select

from src.commons.CommonFunctions import retry_on_ssl_error, pad_text, convert_to_png, \
    check_if_user_can_interact_with_view, interaction_guard
from src.commons.CommonViewComponents import create_close_button, create_dummy_label_button
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous
from src.discord.game_features.player_profile.PlayerProfileImageFactory import PLAYER_PROFILE_TAB_CLOSED
from src.discord.general.handlers.AvatarUnlockHandler import AvatarUnlockHandler
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import TGOMMO_RARITY_MYTHICAL


class UpdatePlayerProfileView(BaseView):
    def __init__(self, message_author, player_profile_image_factory=None, original_view=None, interaction: discord.Interaction=None, original_message=None):
        super().__init__(message_author=message_author, target_user=message_author, image_factory=player_profile_image_factory, original_view=original_view)

        # LOAD VARIABLES
        self.interaction = interaction
        self.original_message = original_message

        self.unlocked_avatars = get_tgommo_db_handler().get_unlocked_avatars_by_user_id(self.message_author.user_id)

        self.avatar_page_capacity = 25
        self.avatar_dropdown_page_num = 1
        self.avatar_dropdown_total_pages = ((len(self.unlocked_avatars) - 1) // self.avatar_page_capacity) + 1
        self.user_creature_collection = get_tgommo_db_handler().get_user_creatures_by_user_id(user_id=self.message_author.user_id)

        # variables for temporary storage of user inputs before they are saved to the database
        self.new_nickname = self.target_user.nickname
        self.new_avatar_id = self.target_user.avatar.avatar_id
        self.new_background_id = self.target_user.background_id
        self.new_creature_slot_id_1 = self.target_user.creature_slot_id_1
        self.new_creature_slot_id_2 = self.target_user.creature_slot_id_2
        self.new_creature_slot_id_3 = self.target_user.creature_slot_id_3
        self.new_creature_slot_id_4 = self.target_user.creature_slot_id_4
        self.new_creature_slot_id_5 = self.target_user.creature_slot_id_5
        self.new_creature_slot_id_6 = self.target_user.creature_slot_id_6

        # LOAD VIEW COMPONENTS
        # BUTTONS
        self.next_avatars_button = self.create_avatar_dropdown_navigation_button(is_next=True, row=0)
        self.previous_avatars_button = self.create_avatar_dropdown_navigation_button(is_next=False, row=0)
        self.placeholder_avatar_options_button = create_dummy_label_button(label_text=f"-----Avatars-----", row=0)

        self.update_profile_button_1 = self.create_update_profile_button(page=1, row=2)
        self.update_profile_button_2 = self.create_update_profile_button(page=2,row=2)

        self.display_creatures_button = self.display_creature_collection_button(row=3)

        self.save_changes_button = self.create_save_changes_button(row=4)
        self.close_button = create_close_button(message_author_id=self.message_author.user_id, interaction_lock=self.interaction_lock, row=4)

        # DROPDOWNS
        self.avatar_picker_dropdown = self.create_avatar_picker_dropdown(row=1)
        background_picker_dropdown = self.create_background_picker_dropdown(row=2)

        # ADD COMPONENTS TO VIEW
        self.rebuild_view()


    # CREATE BUTTONS
    def create_avatar_dropdown_navigation_button(self, is_next, row=0):
        button = Button(label="➡️" if is_next else "⬅️", style=discord.ButtonStyle.blurple, row=row)
        button.callback = self.nav_callback(new_page=next_ if is_next else previous)
        return button
    def nav_callback(self, new_page):
        @interaction_guard(self)
        async def callback(interaction):
            self.avatar_dropdown_page_num += 1 if new_page == next_ else -1
            self.refresh_view()
            await interaction.message.edit(view=self)
        return callback

    def create_update_profile_button(self, page, row=0):
        button = Button(label=f"Change Profile - {page}", style=discord.ButtonStyle.blurple, row=row)
        button.callback = self.update_profile_button_callback_page_1 if page == 1 else self.update_profile_button_callback_page_2
        return button

    def update_profile_button_callback_page_1(self):
        @interaction_guard(self)
        async def callback(interaction):
            display_name_input = TextInput(label="DisplayName", default=f"{self.new_nickname}", placeholder="Set your display name", max_length=20, required=False)
            display_creature_1_input = TextInput(label="Display Creature 1", default=f"{self.new_creature_slot_id_1 if self.new_creature_slot_id_1 != -1 else ''}", placeholder="Set creature ID for slot 1 (use 'See Creature Storage' to view options)", max_length=20, required=False)
            display_creature_2_input = TextInput(label="Display Creature 2", default=f"{self.new_creature_slot_id_2 if self.new_creature_slot_id_2 != -1 else ''}", placeholder="Set creature ID for slot 2 (use 'See Creature Storage' to view options)", max_length=20, required=False)
            display_creature_3_input = TextInput(label="Display Creature 3", default=f"{self.new_creature_slot_id_3 if self.new_creature_slot_id_3 != -1 else ''}",placeholder="Set creature ID for slot 3 (use 'See Creature Storage' to view options)", max_length=20, required=False)
            await interaction.response.send_modal(self.create_user_details_modal(options=(display_name_input, display_creature_1_input, display_creature_2_input, display_creature_3_input)))
        return callback

    def update_profile_button_callback_page_2(self):
        @interaction_guard(self)
        async def callback(interaction):
            display_creature_4_input = TextInput(label="Display Creature 4", default=f"{self.new_creature_slot_id_4 if self.new_creature_slot_id_4 != -1 else ''}",placeholder="Set creature ID for slot 4 (use 'See Creature Storage' to view options)",max_length=20, required=False)
            display_creature_5_input = TextInput(label="Display Creature 5", default=f"{self.new_creature_slot_id_5 if self.new_creature_slot_id_5 != -1 else ''}",placeholder="Set creature ID for slot 5 (use 'See Creature Storage' to view options)",max_length=20, required=False)
            display_creature_6_input = TextInput(label="Display Creature 6", default=f"{self.new_creature_slot_id_6 if self.new_creature_slot_id_6 != -1 else ''}",placeholder="Set creature ID for slot 6 (use 'See Creature Storage' to view options)",max_length=20, required=False)
            await interaction.response.send_modal(self.create_user_details_modal(options=(display_creature_4_input, display_creature_5_input, display_creature_6_input)))
        return callback

    def create_save_changes_button(self, row=0):
        button = Button(label="Save Changes", style=discord.ButtonStyle.green, row=row)
        button.callback = self.save_changes_button_callback
        return button
    def save_changes_button_callback(self,):
        @interaction_guard(self)
        async def callback(interaction):
            await self.handle_invalid_creature_ids(interaction)

            creature_slot_1 = int(self.new_creature_slot_id_1) if self.new_creature_slot_id_1 != '' else -1
            creature_slot_2 = int(self.new_creature_slot_id_2) if self.new_creature_slot_id_2 != '' else -1
            creature_slot_3 = int(self.new_creature_slot_id_3) if self.new_creature_slot_id_3 != '' else -1
            creature_slot_4 = int(self.new_creature_slot_id_4) if self.new_creature_slot_id_4  != '' else -1
            creature_slot_5 = int(self.new_creature_slot_id_5) if self.new_creature_slot_id_5 != '' else -1
            creature_slot_6 = int(self.new_creature_slot_id_6) if self.new_creature_slot_id_6 != '' else -1

            get_tgommo_db_handler().update_user_profile(params=(self.new_nickname, self.new_avatar_id, self.new_background_id, creature_slot_1, creature_slot_2, creature_slot_3, creature_slot_4, creature_slot_5, creature_slot_6, self.target_user.currency, self.target_user.available_catches, self.target_user.rod_level, self.target_user.rod_amount, self.target_user.trap_level, self.target_user.trap_amount, self.target_user.user_id))
            updated_user = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.target_user.user_id)
            self.target_user = updated_user
            self.image_factory.target_user = updated_user

            await self.original_message.edit(attachments=[self.reload_image()], view=self.original_view)
            await interaction.response.send_message("Changes successfully saved!", ephemeral=True)

            await AvatarUnlockHandler(user_id=interaction.user.id, nickname=self.target_user.nickname, interaction=interaction).check_avatar_unlock_conditions()
            await interaction.message.delete(delay=2)


    def display_creature_collection_button(self, row=0):
        button = Button(label="See Creature Storage", style=discord.ButtonStyle.red, row=row)
        button.callback = self.display_creature_collection_callback
        return button
    def display_creature_collection_callback(self,):
        @interaction_guard(self)
        async def callback(interaction):
            await self.build_user_creature_collection(interaction)


    # CREATE MODALS
    def create_user_details_modal(self, options):
        user_details_modal = Modal(title="Update Profile Details")
        for option in options:
            user_details_modal.add_item(option)
        user_details_modal.on_submit = self.user_details_modal_on_submit
        return user_details_modal
    def user_details_modal_on_submit(self,):
        @interaction_guard(self)
        async def callback(interaction):
            for component_row in interaction.data.get('components', []):
                for component in component_row.get('components', []):
                    field_label = component.get('custom_id', '')
                    field_value = component.get('value', '')

                    if 'DisplayName' in field_label and field_value.strip() != '':
                        self.target_user.nickname = field_value.strip()
                    elif 'Display Creature 1' in field_label:
                        self.target_user.creature_slot_id_1 = field_value.strip() if field_value.strip() else ''
                    elif 'Display Creature 2' in field_label:
                        self.target_user.creature_slot_id_1 = field_value.strip() if field_value.strip() else ''
                    elif 'Display Creature 3' in field_label:
                        self.target_user.creature_slot_id_3 = field_value.strip() if field_value.strip() else ''
                    elif 'Display Creature 4' in field_label:
                        self.target_user.creature_slot_id_4 = field_value.strip() if field_value.strip() else ''
                    elif 'Display Creature 5' in field_label:
                        self.target_user.creature_slot_id_5 = field_value.strip() if field_value.strip() else ''
                    elif 'Display Creature 6' in field_label:
                        self.target_user.creature_slot_id_6 = field_value.strip() if field_value.strip() else ''
            await interaction.response.send_message(f"Successfully modified player info - Remember to save your changes!", ephemeral=True)

    # CREATE DROPDOWNS
    def create_avatar_picker_dropdown(self, row=1):
        dropdown = Select(placeholder="Choose Avatar", options=self.get_avatar_dropdown_options(), min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    def avatar_dropdown_callback(self,):
        @interaction_guard(self)
        async def callback(interaction):
            self.new_avatar_id = interaction.data["values"][0]

    def create_background_picker_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Background {i}", value=str(i)) for i in range(1, 2)]
        dropdown = Select(placeholder="Choose Background Style", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown
    @retry_on_ssl_error(max_retries=3, delay=1)
    def background_dropdown_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            # Access the selected value from the interaction
            self.new_background_id = int(interaction.data["values"][0])


    # SUPPORT FUNCTIONS
    # todo: move this to a separate class that can be used by other views that need to display the user's creature collection
    async def build_user_creature_collection(self, interaction: discord.Interaction):
        page_num = 0
        pages = [f"Total Unique Creatures Caught: {len(self.user_creature_collection)}"]
        ordered_creatures = sorted(self.user_creature_collection, key=lambda c: c.dex_no)

        # add an entry for each creature in collection
        for creature_index, creature in enumerate(ordered_creatures):
            current_page = pages[page_num]

            creature_name = f'{creature.name}{f' -  {creature.variant_name}' if creature.variant_name != '' else ''}'
            emojiis = f"{'✨' if creature.local_rarity.name == TGOMMO_RARITY_MYTHICAL else '' }{ '💖' if creature.is_favorite else ''}{ '❗' if creature.nickname else ''}"
            nickname = f"**__{creature.nickname}__**" if creature.nickname != '' else creature.name

            newlines = f'{'\n' if creature.creature_id != ordered_creatures[creature_index - 1].creature_id else ''}\n'
            new_entry = f"{newlines}{creature_index + 1}.  \t\t [{creature.catch_id}] \t ({pad_text(creature_name, 20)}) \t {pad_text(f"{emojiis}{nickname}", 20)}"

            # if the amount of characters passes 1900, move to a new message
            if len(current_page) + len(new_entry) > 1900:
                page_num += 1
                pages.append('')

            pages[page_num] += new_entry

        # Send the first page as the response
        text = f"\n# {self.target_user.nickname}'s Creature Collection (1/{len(pages)}):\n{pages[0]}"
        await interaction.response.send_message(text, ephemeral=True)

        # create page images for user to see
        for page_index, page in enumerate(pages):
            if page_index == 0:
                continue

            text = f"\n# {self.target_user.nickname}'s Creature Collection ({page_index + 1}/{len(pages)}):\n{page}"
            await interaction.followup.send(text, ephemeral=True)

    async def handle_invalid_creature_ids(self, interaction: discord.Interaction):
        warnings = ["_⚠️**WARNING:**⚠️_\n"]

        has_violations, invalid_ids, duplicates, unowned_creatures = self.validate_creature_ids()
        if not has_violations:
            return

        violations_to_reset = []

        if invalid_ids:
            invalid_positions = ', '.join(str(pos) for _, pos in invalid_ids)
            warnings.append(f"* Invalid creature IDs found at positions:\t{invalid_positions}")
            violations_to_reset.extend(invalid_ids)
        if duplicates:
            duplicate_positions = ', '.join(str(pos) for _, pos in duplicates)
            warnings.append(f"* Duplicate creature IDs found at positions:\t{duplicate_positions}")
            violations_to_reset.extend(duplicates)
        if unowned_creatures:
            violation_positions = ', '.join(str(pos) for _, pos in unowned_creatures)
            warnings.append(
                f"* You do not own the creatures in the following display positions:\t{violation_positions}")
            violations_to_reset.extend(unowned_creatures)

        warnings.append("\n These positions were reset to empty.")
        self.reset_display_creature_ids(violations_to_reset)

        warning_message = '\n'.join(warnings)
        await interaction.response.send_message(warning_message, ephemeral=True)

    def validate_creature_ids(self):
        invalid_ids = []
        duplicates = []
        unowned_creatures = []
        seen_ids = []

        display_creature_ids = [(self.new_creature_slot_id_1, 1), (self.new_creature_slot_id_2, 2), (self.new_creature_slot_id_3, 3), (self.new_creature_slot_id_4, 4), (self.new_creature_slot_id_5, 5), (self.new_creature_slot_id_6, 6)]

        for creature_id, pos in display_creature_ids:
            # Skip empty slots
            if not creature_id or str(creature_id) == "-1":
                continue

            # Check for invalid format (non-integer or non-positive)
            try:
                id_as_int = int(creature_id)
                if id_as_int <= 0:
                    invalid_ids.append((creature_id, pos))
                    continue
            except ValueError:
                invalid_ids.append((creature_id, pos))
                continue

            # Check for duplicates
            if creature_id in seen_ids:
                duplicates.append((creature_id, pos))
            else:
                seen_ids.append(creature_id)

            # Check if user owns the creature
            if not any(str(creature.catch_id) == str(creature_id) for creature in self.user_creature_collection):
                unowned_creatures.append((creature_id, pos))

        has_violations = len(invalid_ids) > 0 or len(duplicates) > 0 or len(unowned_creatures) > 0
        return has_violations, invalid_ids, duplicates, unowned_creatures

    def reset_display_creature_ids(self, positions):
        # Create attribute mapping for easier setting
        creature_id_attrs = {1: 'creature_id_1', 2: 'creature_id_2', 3: 'creature_id_3', 4: 'creature_id_4', 5: 'creature_id_5', 6: 'creature_id_6'}

        # For each duplicate ID, clear all but the first occurrence
        for duplicate_id, position in positions:
            setattr(self, creature_id_attrs[position], "-1")


    # BUILD VIEW CONTENT
    def update_view_items(self):
        first_index = ((self.avatar_dropdown_page_num - 1) * self.avatar_page_capacity) + 1
        last_index = min(self.avatar_dropdown_page_num * self.avatar_page_capacity, len(self.unlocked_avatars))
        self.placeholder_avatar_options_button.label = f"-----Avatars ({first_index} - {last_index})-----"

        self.next_avatars_button.disabled = self.avatar_dropdown_page_num >= self.avatar_dropdown_total_pages
        self.previous_avatars_button.disabled = self.avatar_dropdown_page_num == 1

        self.avatar_picker_dropdown.options = self.get_avatar_dropdown_options()
    def rebuild_view(self):
        self.clear_items()

        # row 1
        if len(self.unlocked_avatars) > self.avatar_page_capacity:
            self.add_item(self.previous_avatars_button)
            self.add_item(self.placeholder_avatar_options_button)
            self.add_item(self.next_avatars_button)
        # row 1
        self.add_item(self.avatar_picker_dropdown)
        # row 2
        self.add_item(create_dummy_label_button(label_text="Update Profile:", row=2))
        self.add_item(self.update_profile_button_1)
        self.add_item(self.update_profile_button_2)
        # row 3
        self.add_item(self.display_creatures_button)
        # row 4
        self.add_item(self.save_changes_button)
        self.add_item(self.close_button)

    # Support functions
    def get_avatar_dropdown_options(self):
        first_index = ((self.avatar_dropdown_page_num - 1) * self.avatar_page_capacity)
        last_index = min(self.avatar_dropdown_page_num * self.avatar_page_capacity, len(self.unlocked_avatars))
        return [discord.SelectOption(label=f"Avatar {i+1} - {self.unlocked_avatars[i].name}", value=str(self.unlocked_avatars[i].avatar_id)) for i in range(first_index, last_index)]

    def reload_image(self):
        new_image = self.image_factory.reload_image(open_tab=PLAYER_PROFILE_TAB_CLOSED)
        return convert_to_png(new_image, 'player_profile_image.png')

