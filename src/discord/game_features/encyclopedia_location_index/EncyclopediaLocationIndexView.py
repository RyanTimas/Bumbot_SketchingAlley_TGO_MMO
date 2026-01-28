import asyncio
import discord
from discord.ui import Select
from sqlalchemy import false

from src.commons.CommonFunctions import convert_to_png, create_go_back_button, create_close_button
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.discord.game_features.encyclopedia.EncyclopediaView import EncyclopediaView, next_, previous, jump
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexImageFactory import EncyclopediaLocationIndexImageFactory
from src.discord.objects.TGOEnvironment import NATIONAL_ENV

class EncyclopediaLocationIndexView(discord.ui.View):
    def __init__(self, message_author, encyclopedia_location_index_image_factory: EncyclopediaLocationIndexImageFactory, target_user=None, original_view=None):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.target_user = target_user if target_user else None

        self.encyclopedia_location_index_image_factory = encyclopedia_location_index_image_factory
        self.encyclopedia_location_index_image_factory.build_encyclopedia_location_index_page_image()

        self.original_view = original_view
        self.interaction_lock = asyncio.Lock()

        self.new_page = 1

        self.selectable_environments = get_tgommo_db_handler().get_all_environments_in_rotation()
        self.selectable_environments.insert(0, NATIONAL_ENV)
        self.selected_environment = self.selectable_environments[0] if self.selectable_environments else None

        # INITIALIZE BUTTONS AND DROPDOWNS
        self.page_jump_dropdown = self.create_page_jump_dropdown(row=0)

        self.prev_button = self.create_navigation_button(is_next=False, row=1)
        self.next_button = self.create_navigation_button(is_next=True, row=1)

        self.environment_dropdown = self.create_environments_dropdown(row=2)

        self.view_environment_button = self.create_view_environment_button(row=3)

        self.close_button = create_close_button(interaction_lock=self.interaction_lock, message_author_id=self.message_author.id, row=4)
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=4, interaction_lock=self.interaction_lock, message_author_id=self.message_author.id)

        # Add buttons to view
        self.refresh_view()


    # CREATE BUTTONS
    def create_navigation_button(self, is_next, row=0):
        button = discord.ui.Button(
            label="To Next Page➡️" if is_next else "⬅️To Previous Page",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=next_ if is_next else previous)
        return button
    def nav_callback(self, new_page,):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                # Update page number
                page_options = {
                    next_: self.encyclopedia_location_index_image_factory.page_num + 1,
                    previous: self.encyclopedia_location_index_image_factory.page_num -1,
                    jump: self.new_page
                }

                new_image = self.encyclopedia_location_index_image_factory.build_encyclopedia_location_index_page_image(new_page_number=page_options[new_page])

                # Update state and button appearance
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'encyclopedia_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_view_environment_button(self, row=4):
        button = discord.ui.Button(
            label="View Environment Encyclopedia",
            style=discord.ButtonStyle.green,
            row=row,
        )
        button.callback = self.view_environment_callback
        return button
    async def view_environment_callback(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
            return

        async with self.interaction_lock:
            await interaction.response.defer()

            # Create encyclopedia view for the selected environment
            encyclopedia_img_factory = EncyclopediaImageFactory(environment=self.selected_environment if self.selected_environment else NATIONAL_ENV, message_author=self.message_author, target_user=self.target_user,)
            encyclopedia_view = EncyclopediaView(encyclopedia_image_factory=encyclopedia_img_factory, message_author=self.message_author, original_view=self, original_image_files=[convert_to_png(self.encyclopedia_location_index_image_factory.build_encyclopedia_location_index_page_image(), f'encyclopedia_location_index_page.png')],)
            await interaction.message.edit(attachments=[convert_to_png(encyclopedia_img_factory.build_encyclopedia_page_image(), f'encyclopedia_page.png')], view=encyclopedia_view)

            self.selected_environment = NATIONAL_ENV


    # CREATE DROPDOWNS
    def create_page_jump_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, self.encyclopedia_location_index_image_factory.total_pages)]
        dropdown = Select(placeholder="Skip to Page", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.page_jump_callback
        return dropdown
    async def page_jump_callback(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
            return

        async with self.interaction_lock:
            await interaction.response.defer()

            self.new_page = int(interaction.data["values"][0])
            new_image = self.encyclopedia_location_index_image_factory.build_encyclopedia_location_index_page_image(new_page_number=self.new_page)
            self.update_button_states()

            await interaction.message.edit(attachments=[convert_to_png(new_image, f'encyclopedia_page.png')], view=self)

    def create_environments_dropdown(self, row=0):
        options = [
            discord.SelectOption(
                label=env.name,  # name
                value=str(env.environment_id),
                description=env.location
            )
            for env in self.selectable_environments[:25]  # Discord limit of 25 options
        ]

        dropdown = Select(
            placeholder=self.selectable_environments[0].name if self.selectable_environments else "No Environments Available",
            options=options,
            min_values=0,
            max_values=1,
            row=row,
        )
        dropdown.callback = self.environments_dropdown_callback
        return dropdown
    async def environments_dropdown_callback(self, interaction: discord.Interaction):
        if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
            return

        async with self.interaction_lock:
            await interaction.response.defer()

            environment_id = int(interaction.data["values"][0]) if interaction.data["values"] else None
            self.selected_environment = get_tgommo_db_handler().get_environment_by_id(environment_id=environment_id) if environment_id > 0 else NATIONAL_ENV


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        # Update navigation buttons
        current_page = self.encyclopedia_location_index_image_factory.page_num
        total_pages = self.encyclopedia_location_index_image_factory.total_pages

        self.page_jump_dropdown.options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, total_pages + 1)]
        self.page_jump_dropdown.placeholder = f"Page {current_page}"
        self.page_jump_dropdown.disabled = total_pages == 1

        self.prev_button.disabled = current_page == 1
        self.next_button.disabled = current_page == total_pages
    def rebuild_view(self):
        for item in self.children.copy():
            self.remove_item(item)

        # Add buttons to view
        if len(self.selectable_environments) > 8:
            self.add_item(self.page_jump_dropdown)

            self.add_item(self.prev_button)
            self.add_item(self.next_button)

        self.add_item(self.environment_dropdown)
        self.add_item(self.view_environment_button)

        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)