import discord
from discord.ui import Select

from src.commons.CommonFunctions import convert_to_png, interaction_guard
from src.commons.CommonFunctions import retry_on_ssl_error
from src.commons.CommonViewComponents import create_go_back_button, create_close_button, create_navigation_button
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.discord.game_features.encyclopedia.EncyclopediaView import EncyclopediaView
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexImageFactory import \
    EncyclopediaLocationIndexImageFactory
from src.discord.general.template.BaseView import BaseView
from src.discord.objects.TGOEnvironment import NATIONAL_ENV


class EncyclopediaLocationIndexView(BaseView):
    def __init__(self, message_author, target_user, encyclopedia_location_index_image_factory: EncyclopediaLocationIndexImageFactory, original_view=None):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=encyclopedia_location_index_image_factory, original_view=original_view)
        self.selectable_environments = get_tgommo_db_handler().get_all_environments_in_rotation()
        self.selectable_environments.insert(0, NATIONAL_ENV)
        self.selected_environment = self.selectable_environments[0]

        self.encyclopedia_img_factory = EncyclopediaImageFactory(environment=self.selected_environment if self.selected_environment else NATIONAL_ENV, message_author=self.message_author, target_user=self.target_user,)
        self.encyclopedia_view = EncyclopediaView(message_author=self.message_author, target_user=self.target_user, encyclopedia_image_factory=self.encyclopedia_img_factory, original_view=self, original_image_files=[self.reload_image()])

        # INITIALIZE BUTTONS AND DROPDOWNS
        self.environment_dropdown = self.create_environments_dropdown(row=2)
        self.view_environment_button = self.create_view_environment_button(row=3)

        # Add buttons to view
        self.refresh_view()


    # CREATE BUTTONS
    def create_view_environment_button(self, row=4):
        button = discord.ui.Button(label="View Environment Encyclopedia", style=discord.ButtonStyle.green, row=row,)
        button.callback = self.view_environment_callback()
        return button
    def view_environment_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            # Set the selected environment in the encyclopedia image factory to ensure the correct environment is displayed when returning to location index view
            self.encyclopedia_img_factory.load_relevant_info(environment=self.selected_environment)
            self.encyclopedia_view.refresh_view()
            await interaction.message.edit(attachments=[self.reload_encyclopedia_image()], view=self.encyclopedia_view)
            self.selected_environment = NATIONAL_ENV
        return callback

    def create_environments_dropdown(self, row=0):
        options = [
            discord.SelectOption(label=env.name,  value=str(env.environment_id), description=env.location)
            for env in self.selectable_environments[:25]  # Discord limit of 25 options
        ]
        dropdown = Select(placeholder=self.selectable_environments[0].name, options=options, min_values=0, max_values=1, row=row,)

        dropdown.callback = self.environments_dropdown_callback()
        return dropdown
    def environments_dropdown_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            environment_id = int(interaction.data["values"][0]) if interaction.data["values"] else None
            self.selected_environment = get_tgommo_db_handler().get_environment_by_id(environment_id=environment_id) if environment_id > 0 else NATIONAL_ENV
        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def update_button_states(self):
        # Update navigation buttons
        self.page_jump_dropdown.options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, self.image_factory.total_pages + 1)]
        self.page_jump_dropdown.placeholder = f"Page {self.image_factory.page_num}"
        self.page_jump_dropdown.disabled = self.image_factory.total_pages == 1

        self.prev_button.disabled = self.image_factory.page_num == 1
        self.next_button.disabled = self.image_factory.page_num == self.image_factory.total_pages
    def rebuild_view(self):
        super().rebuild_view()
        self.clear_items()

        # Add buttons to view
        self.add_item(self.environment_dropdown)
        self.add_item(self.view_environment_button)

        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)

    def reload_encyclopedia_image(self, new_page_number=None):
        new_image = self.encyclopedia_img_factory.reload_image(new_page_number=new_page_number, environment=self.selected_environment)
        return convert_to_png(new_image, 'encyclopedia_image.png')
