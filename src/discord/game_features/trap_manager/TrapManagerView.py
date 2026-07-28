from src.commons.CommonDecorators import interaction_guard
from src.commons.CommonViews import ConfirmationView
from src.discord.game_features.player_profile.PlayerProfileImageFactory import *
from src.discord.game_features.trap_manager.TrapManagerImageFactory import TrapManagerImageFactory
from src.discord.general.template.BaseView import BaseView
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler


class TrapManagerView(BaseView):
    def __init__(self, message_author, trap_manager_image_factory: TrapManagerImageFactory, original_view=None):
        super().__init__(message_author=message_author, target_user=message_author, image_factory=trap_manager_image_factory, original_view=original_view)

        # View Variables
        self.active_option = TRAP_MANAGER_OPEN_OPTION_DEFAULT

        # View Items
        # row 0
        self.swap_tab_button = self.create_swap_tab_button(row=0)
        self.battery_charge_button = self.create_battery_charge_button(row=0)
        # row 1
        self.page_jump_dropdown.row = 1
        self.trap_swap_dropdown = self.create_active_trap_swap_dropdown(row=1)
        # row 2
        self.trap_mode_swap_dropdown = self.create_trap_mode_swap_dropdown(row=2)

        # Add buttons to view
        super().refresh_view()

    ''' ----- VIEW COMPONENTS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # ------ BUTTONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def create_swap_tab_button(self, row=1):
        button = discord.ui.Button(label=f"Swap to {TRAP_MANAGER_OPEN_TAB_CAPTURES  if self.image_factory.open_tab == TRAP_MANAGER_OPEN_TAB_SUMMARY else TRAP_MANAGER_OPEN_TAB_SUMMARY} View", style=discord.ButtonStyle.success, row=row)
        button.callback = self.swap_tab_callback()
        return button
    def swap_tab_callback(self):
        @interaction_guard()
        async def callback(interaction):
            await interaction.response.defer()

            self.image_factory.open_tab = TRAP_MANAGER_OPEN_TAB_CAPTURES  if self.image_factory.open_tab == TRAP_MANAGER_OPEN_TAB_SUMMARY else TRAP_MANAGER_OPEN_TAB_SUMMARY

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_battery_charge_button(self, row=1):
        button = discord.ui.Button(label="Trap Fully Charged" if self.image_factory.player_trap_link.player_trap_charges == self.image_factory.player_trap_link.player_max_trap_charges else "Use Battery (+8 charges)", style=discord.ButtonStyle.primary, row=row)
        button.callback = self.battery_charge_callback()
        return button
    def battery_charge_callback(self):
        @interaction_guard()
        async def callback(interaction):
            if self.image_factory.player_trap_link.player_trap_charges >= self.image_factory.player_trap_link.player_max_trap_charges:
                await interaction.response.send_message("Your trap charges are already full.", ephemeral=True)
                return

            increment = 8
            proposed_total = self.image_factory.player_trap_link.player_trap_charges + increment
            actual_total = min(proposed_total, self.image_factory.player_trap_link.player_max_trap_charges)
            wasted = max(proposed_total - self.image_factory.player_trap_link.player_max_trap_charges, 0)

            user_battery = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=ITEM_ID_BATTERY)
            batteries_available = user_battery.item_quantity if user_battery else 0

            if wasted > 0:
                prompt = f"You have {batteries_available} batter{"y" if batteries_available == 1 else "ies"} remaining.\nUse a battery to add {increment-wasted} charges to {self.image_factory.active_trap.item_name}? \nResulting charges: {actual_total}/{self.image_factory.player_trap_link.player_max_trap_charges}.\n\n## ❗{wasted} charges will be wasted because your trap's max capacity is {self.image_factory.player_trap_link.player_max_trap_charges} charges.❗\nUse a battery anyway?"
            else:
                prompt = f"You have {batteries_available} batter{"y" if batteries_available == 1 else "ies"} remaining.\nUse a battery to add {increment} charges to {self.image_factory.active_trap.item_name}?\nResulting charges: {actual_total}/{self.image_factory.player_trap_link.player_max_trap_charges}."

            # capture the original persistent trap manager message so handlers can edit it later
            original_trap_manager_message = interaction.message

            # create confirm handler that will be called when view button pressed
            async def _on_confirm(inter: discord.Interaction):
                battery_total = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=ITEM_ID_BATTERY).item_quantity
                if battery_total >= 0:
                    self.image_factory.player_trap_link.player_trap_charges = actual_total
                    get_tgommo_db_handler().update_user_trap_link_charges(user_id=self.message_author.user_id, player_trap_charges=actual_total)
                    get_tgommo_db_handler().update_user_profile_available_items(user_id=self.message_author.user_id, item_id=ITEM_ID_BATTERY, new_amount=battery_total-1)
                else:
                    await inter.followup.send("You don't have any batteries to use.", ephemeral=True)
                    return

                # refresh view image and edit the original trap manager message
                self.refresh_view()
                await original_trap_manager_message.edit(attachments=[self.reload_image()], view=self)
                await inter.followup.send(f"Battery used. Charges are now {actual_total}/{self.image_factory.player_trap_link.player_max_trap_charges}.", ephemeral=True)

            await interaction.response.send_message(prompt, view=ConfirmationView(original_view=self, original_message=original_trap_manager_message, on_confirm=_on_confirm), ephemeral=True)
        return callback

    def create_mode_swap_button(self, row=1):
        button = discord.ui.Button(label="Open Trap Mode Options", style=discord.ButtonStyle.success, row=row)
        button.callback = self.swap_tab_callback()
        return button

    # ------ DROPDOWNS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def create_active_trap_swap_dropdown(self, row=2):
        options = [discord.SelectOption(label=f"{trap.item_name}", value=f"{trap.item_id}",) for trap in self.image_factory.available_traps]
        if not options:
            options.append(discord.SelectOption(label="No traps available.", value="none"))

        dropdown = discord.ui.Select(placeholder=f"Swap Trap ({self.image_factory.active_trap.item_name} Currently Active)", options=options[:25], row=row)
        dropdown.callback = self.active_trap_swap_select_callback()
        return dropdown
    def active_trap_swap_select_callback(self):
        @interaction_guard()
        async def callback(interaction):
            await interaction.response.defer()
            selected_value = interaction.data['values'][0]

            if selected_value != self.image_factory.active_trap.item_id:
                original_trap_manager_message = interaction.message

                # create confirm handler that will be called when view button pressed
                async def _on_confirm(inter: discord.Interaction):
                    # update data
                    new_active_trap = next((trap for trap in self.image_factory.available_traps if trap.item_id == selected_value), None)
                    self.image_factory.active_trap = new_active_trap
                    get_tgommo_db_handler().update_user_trap_link_item_id(user_id=self.message_author.user_id, item_id=new_active_trap.item_id)

                    # refresh view image and edit the original trap manager message
                    self.refresh_view()
                    await original_trap_manager_message.edit(attachments=[self.reload_image()], view=self)
                    await inter.followup.send(f"🚨 Swap Active Trap ({self.image_factory.active_trap.item_name} Currently Active", files=[convert_to_png(new_active_trap.item_image, "camera_image.png")], ephemeral=True)
                await interaction.followup.send("Are you sure you want to switch traps? All remaining battery charges will transfer to your new trap.", view=ConfirmationView(original_view=self, original_message=original_trap_manager_message, on_confirm=_on_confirm), ephemeral=True)
        return callback

    def create_trap_mode_swap_dropdown(self, row=2):
        options = [discord.SelectOption(label=str(mode), value=str(mode)) for mode in ACTIVE_TRAP_MODES_LIST]

        if not options:
            options.append(discord.SelectOption(label="No modes available.", value="none"))

        dropdown = discord.ui.Select(placeholder=f"🔋 Swap Trap Mode (Currently in {self.image_factory.player_trap_link.active_trap_mode} Mode)", options=options[:25], row=row)
        dropdown.callback = self.trap_mode_swap_select_callback()
        return dropdown
    def trap_mode_swap_select_callback(self):
        @interaction_guard()
        async def callback(interaction):
            await interaction.response.defer()
            selected_value = interaction.data['values'][0]

            if selected_value != self.image_factory.player_trap_link.active_trap_mode:
                original_trap_manager_message = interaction.message

                # create confirm handler that will be called when view button pressed
                async def _on_confirm(inter: discord.Interaction):
                    # update data
                    self.image_factory.player_trap_link.active_trap_mode = selected_value
                    get_tgommo_db_handler().update_user_trap_link_active_trap_mode(user_id=self.message_author.user_id, active_trap_mode=selected_value)

                    # refresh view image and edit the original trap manager message
                    self.refresh_view()
                    await original_trap_manager_message.edit(attachments=[self.reload_image()], view=self)
                    await inter.followup.send(f"Trap is now in {selected_value} mode.", ephemeral=True)
                await interaction.followup.send(f"Are you sure you want to switch trap to **{selected_value}** mode?", view=ConfirmationView(original_view=self, original_message=original_trap_manager_message, on_confirm=_on_confirm), ephemeral=True)
        return callback


    ''' ----- SUPPORT FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def update_view_items(self):
        super().update_view_items()

        # update labels
        self.battery_charge_button.label = "Trap Fully Charged" if self.image_factory.player_trap_link.player_trap_charges == self.image_factory.player_trap_link.player_max_trap_charges else "Use Battery (+8 charges)"
        self.swap_tab_button.label = f"Swap to {TRAP_MANAGER_OPEN_TAB_CAPTURES  if self.image_factory.open_tab == TRAP_MANAGER_OPEN_TAB_SUMMARY else TRAP_MANAGER_OPEN_TAB_SUMMARY} View"
        self.trap_swap_dropdown.placeholder = f"🚨 Swap Active Trap ({self.image_factory.active_trap.item_name} Currently Active)"
        self.trap_mode_swap_dropdown.placeholder = f"🔋 Swap Trap Mode (Currently in {self.image_factory.player_trap_link.active_trap_mode} Mode)"

        # update disabled states
        self.battery_charge_button.disabled = self.image_factory.player_trap_link.player_trap_charges == self.image_factory.player_trap_link.player_max_trap_charges
    def rebuild_view(self):
        self.clear_items()

        if self.image_factory.open_tab == TRAP_MANAGER_OPEN_TAB_SUMMARY:
            # row 0
            self.add_item(self.swap_tab_button)
            self.add_item(self.battery_charge_button)
            # row 1
            self.add_item(self.trap_swap_dropdown)
            # row 2
            self.add_item(self.trap_mode_swap_dropdown)
        elif self.image_factory.open_tab == TRAP_MANAGER_OPEN_TAB_CAPTURES:
            self.add_item(self.swap_tab_button)
            self.add_item(self.page_jump_dropdown)

        # Add action components
        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)
            
            
    def reload_image(self, target_user= None, new_page_number=None, new_player_trap_link=None):
        new_image = self.image_factory.reload_image(new_page_number=new_page_number, new_player_trap_link=new_player_trap_link)
        return convert_to_png(new_image, 'trap_manager_view.png')


''' ----- SUPPORT CLASSES ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
