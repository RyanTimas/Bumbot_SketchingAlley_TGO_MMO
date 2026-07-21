from src.commons.CommonDecorators import interaction_guard
from src.commons.GameStateManager import get_game_state_manager
from src.discord.game_features.player_profile.PlayerProfileImageFactory import *
from src.discord.game_features.shop.ShopImageFactory import ShopImageFactory
from src.discord.general.template.BaseView import BaseView


class TrapManagerView(BaseView):
    def __init__(self, message_author, trap_manager_image_factory: ShopImageFactory, original_view=None):
        super().__init__(message_author=message_author, target_user=message_author, image_factory=trap_manager_image_factory, original_view=original_view)

        # View Variables


        # View Items


        # Add buttons to view
        super().refresh_view()

    ''' ----- VIEW COMPONENTS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''


    ''' ----- SUPPORT FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def update_view_items(self):
        super().update_view_items()
        # todo: update view items based on the current state of the trap manager

    def rebuild_view(self):
        self.clear_items()

        # row 0

        # row 1


    def reload_image(self, target_user= None, image_factory= None, new_page_number=None):
        new_image = self.image_factory.reload_image()
        return convert_to_png(new_image, 'trap_manager_view.png')


''' ----- SUPPORT CLASSES ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
