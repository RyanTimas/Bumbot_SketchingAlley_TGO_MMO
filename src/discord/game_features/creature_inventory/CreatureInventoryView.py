import asyncio

import discord
from discord.ui import Select

from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view, convert_to_png
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous, jump


class CreatureInventoryView(discord.ui.View):
    def __init__(self, message_author, owner_id, creature_inventory_image_factory: CreatureInventoryImageFactory, original_view=None):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.owner_id = owner_id

        self.creature_inventory_image_factory = creature_inventory_image_factory
        self.original_view = original_view

        self.interaction_lock = asyncio.Lock()
        self.new_box = 1

        # DEFINE VIEW COMPONENTS
        self.box_jump_dropdown = self.create_box_jump_dropdown(row=0)

        self.prev_button = self.create_navigation_button(is_next=False, row=1)
        self.page_jump_button = self.create_advanced_navigation_button(row=1)
        self.next_button = self.create_navigation_button(is_next=True, row=1)

        # self.show_mythics_button = self.create_toggle_mythics_button(row=2)
        # self.show_favorites_button = self.create_toggle_favorites_button(row=2)

        # self.release_button = self.create_release_button(row=3)

        # ADD ITEMS TO VIEW
        # row 0
        self.add_item(self.box_jump_dropdown)
        # row 1
        self.add_item(self.prev_button)
        self.add_item(self.page_jump_button)
        self.add_item(self.next_button)





    def create_navigation_button(self, is_next, row=0):
        button = discord.ui.Button(
            label="To Next Page➡️" if is_next else "⬅️To Previous Page",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=next_ if is_next else previous)
        return button
    def create_advanced_navigation_button(self, row):
        button = discord.ui.Button(
            label="⬆️ Jump To Page ⬆️️",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=jump)
        return button
    def nav_callback(self, new_page, ):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                # Update page number
                page_options = {
                    next_: self.creature_inventory_image_factory.current_box_num + 1,
                    previous: self.creature_inventory_image_factory.current_box_num - 1,
                    jump: self.new_box
                }

                new_image = self.creature_inventory_image_factory.build_creature_inventory_page_image(new_box_number=page_options[new_page])

                # Update state and button appearance
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'player_boxes_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    # CREATE DROPDOWNS
    def create_box_jump_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Box {i}", value=str(i)) for i in range(1, self.creature_inventory_image_factory.total_box_num + 1)]
        dropdown = Select(placeholder="Skip to Box", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown

    async def avatar_dropdown_callback(self, interaction: discord.Interaction):
        self.new_box = int(interaction.data["values"][0])
        await interaction.response.defer()

    # FUNCTIONS FOR UPDATING VIEW STATE
    def update_button_states(self):
        # Update the enabled/disabled state of navigation buttons based on current page
        self.prev_button.disabled = self.creature_inventory_image_factory.current_box_num <= 1
        self.next_button.disabled = self.creature_inventory_image_factory.current_box_num >= self.creature_inventory_image_factory.total_box_num

    # FUNCTIONS FOR UPDATING DATABASE
    def get_released_creatures(self):
        return [creature for creature in self.creatures if creature.is_released]

    def release_creatures(self, creature_ids: list[int]):
        pass

