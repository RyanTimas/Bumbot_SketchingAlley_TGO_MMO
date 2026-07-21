from src.commons.CommonFunctions import *
from src.commons.GameStateManager import game_state_manager, get_game_state_manager
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.player_profile.PlayerProfileSidePanelTabFactory import PlayerProfileSidePanelTabFactory
from src.discord.game_features.shop.ShopItemImageFactory import ShopItemImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *

class TrapManagerImageFactory(BaseImageFactory):
    def __init__(self, message_author):
        super().__init__(message_author=message_author, target_user=message_author)

        # Image Factory Variables

        self.load_relevant_info()

    def build_image(self):
        # todo: build the trap manager image based on the current state of the trap manager
        return

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)
        return