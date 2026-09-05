from src.commons.CommonDecorators import interaction_guard
from src.commons.CommonViews import ConfirmationView
from src.discord.game_features.omnipotent_bait_manager.OmnipotentBaitManagerImageFactory import \
    OmnipotentBaitManagerImageFactory
from src.discord.game_features.player_profile.PlayerProfileImageFactory import *
from src.discord.game_features.trap_manager.TrapManagerImageFactory import TrapManagerImageFactory
from src.discord.general.template.BaseView import BaseView
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.handlers.ItemUseHandler.TrapHandler import TrapHandler
from src.discord.objects.CreatureRarity import MYTHICAL


class OmnipotentBaitManagerView(BaseView):
    def __init__(self, message_author, omnipotent_bait_image_factory: OmnipotentBaitManagerImageFactory, discord_bot=None, original_view=None):
        super().__init__(message_author=message_author, target_user=message_author, image_factory=omnipotent_bait_image_factory, original_view=original_view)

        # View Variables
        self.selected_creature = self.image_factory.creatures[0] if self.image_factory.creatures else None
        self.discord_bot = discord_bot

        # View Items
        # row 0
        # row 1
        self.environment_select_dropdown = self.create_environment_select_dropdown(row=1)
        # row 2
        self.creature_select_dropdown = self.create_creature_select_dropdown(row=2)
        # row 3
        self.creature_select_button = self.create_creature_select_button(row=3)

        # Add buttons to view
        super().refresh_view()

    ''' ----- VIEW COMPONENTS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # ------ BUTTONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def create_creature_select_button(self, row=1):
        button = discord.ui.Button(label="Spawn Creature", style=discord.ButtonStyle.primary, row=row)
        button.callback = self.creature_select_callback()
        return button
    def creature_select_callback(self):
        @interaction_guard()
        async def callback(interaction):
            confirmation_message = f"Are you sure you want to use your Omnipotent Bait to spawn a {self.selected_creature.full_name}?"

            # capture the original persistent trap manager message so handlers can edit it later
            original_trap_manager_message = interaction.message

            # create confirm handler that will be called when view button pressed
            async def _on_confirm(inter: discord.Interaction):
                if random.randint(1, 8) == 1:
                    self.selected_creature.set_creature_rarity(new_rarity=MYTHICAL)

                omnipotent_bait = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT)

                # remove omnipotent bait from user inventory
                if omnipotent_bait.item_quantity <= 0:
                    await inter.followup.send(f"You do not have any Omnipotent Bait left to use!", ephemeral=True)
                    return
                get_tgommo_db_handler().update_user_profile_available_items(user_id=self.message_author.user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT, new_amount=get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT).item_quantity-1)

                # refresh view image and edit the original trap manager message
                self.refresh_view()
                await original_trap_manager_message.edit(attachments=[self.reload_image()], view=self)

                await self.discord_bot.creature_spawner_handler.spawn_creature(user=self.message_author, creature=self.selected_creature)
                await inter.followup.send(f"<@{self.message_author.user_id}> *({self.message_author.nickname})* used the Omnipotent Bait!", ephemeral=True)

                return True, f"<@{self.message_author.user_id}> *({self.message_author.nickname})* used the Omnipotent Bait!"

            await interaction.response.send_message(confirmation_message, files=[convert_to_png(image=self.selected_creature.creature_image, file_name="creature_img.png")], view=ConfirmationView(original_view=self, original_message=original_trap_manager_message, on_confirm=_on_confirm), ephemeral=True)
        return callback

    # ------ DROPDOWNS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def create_creature_select_dropdown(self, row=2):
        options = [discord.SelectOption(label=f"{creature.local_dex_no}{convert_int_to_letter(creature.variant_no) if creature.variant_no != 1 else ""}. {creature.name} {f"({creature.variant_name})"  if creature.variant_no != 1 else ""}", value=creature.creature_id) for creature in self.image_factory.creatures]
        if not options:
            options.append(discord.SelectOption(label="No creatures available.", value="none"))

        low_bound = (self.page_num - 1) * self.image_factory.max_icons_per_page
        high_bound = min((self.page_num - 1) * self.image_factory.max_icons_per_page + self.image_factory.max_icons_per_page, len(self.image_factory.creatures))

        dropdown = discord.ui.Select(placeholder=f"🐾 Selected Creature - {self.selected_creature.full_name}", options=options[low_bound:high_bound], row=row)
        dropdown.callback = self.creature_select_dropdown_callback()
        return dropdown
    def creature_select_dropdown_callback(self):
        @interaction_guard()
        async def callback(interaction):
            await interaction.response.defer()
            self.selected_creature = get_tgommo_db_handler().get_environment_creature_by_environment_id_and_creature_id(creature_id=interaction.data['values'][0], environment_id=self.image_factory.active_environment.environment_id)
            self.selected_creature.environment_id = self.image_factory.active_environment.environment_id
        return callback

    def create_environment_select_dropdown(self, row=2):
        options = [discord.SelectOption(label=f"{environment.dex_no}. {environment.name}", value=environment.environment_id) for environment in get_tgommo_db_handler().get_all_environments_in_rotation()]
        if not options:
            options.append(discord.SelectOption(label="No environments available.", value="none"))

        dropdown = discord.ui.Select(placeholder=f"🌍 Selected Environment - {self.image_factory.active_environment.name}", options=options, row=row)
        dropdown.callback = self.environment_select_dropdown_callback()
        return dropdown
    def environment_select_dropdown_callback(self):
        @interaction_guard()
        async def callback(interaction):
            await interaction.response.defer()

            new_image = self.reload_image(active_environment=get_tgommo_db_handler().get_environment_by_id(interaction.data['values'][0]))
            self.refresh_view()
            await interaction.message.edit(attachments=[new_image], view=self)
        return callback

    ''' ----- SUPPORT FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def update_view_items(self):
        super().update_view_items()

        # update dropdown options
        self.environment_select_dropdown = self.create_environment_select_dropdown(row=1)
        self.creature_select_dropdown = self.create_creature_select_dropdown(row=2)

        # update labels
        self.creature_select_dropdown.placeholder = f"🐾 Selected Creature - {self.selected_creature.full_name}"
        self.environment_select_dropdown.placeholder = f"🌍 Selected Environment - {self.image_factory.active_environment.name}"
    def rebuild_view(self):
        self.clear_items()

        # row 0
        self.add_item(self.page_jump_dropdown)
        # row 1
        self.add_item(self.environment_select_dropdown)
        # row 2
        self.add_item(self.creature_select_dropdown)
        # row 3
        self.add_item(self.creature_select_button)

        # Add action components
        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)
    def reload_image(self, target_user= None, image_factory= None, new_page_number=None, active_environment=None):
        # Forward pagination and environment parameters to the image factory reload so it remains sole owner of pagination state
        new_image = self.image_factory.reload_image(target_user=target_user, new_page_number=new_page_number, active_environment=active_environment)
        return convert_to_png(new_image, 'omnipotent_bait_manager_view.png')


    ''' ----- SUPPORT CLASSES ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''

