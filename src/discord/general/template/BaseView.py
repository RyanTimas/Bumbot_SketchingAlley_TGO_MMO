import asyncio

import discord

from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view, convert_to_png
from src.commons.CommonViewComponents import create_go_back_button, create_close_button
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous
from src.discord.game_features.avatar_board.AvatarBoardImageFactory import AvatarBoardImageFactory, AVATAR_QUESTS, \
    UNLOCKED_AVATARS
from src.discord.objects.TGOPlayer import TGOPlayer


class BaseView(discord.ui.View):
    def __init__(self, message_author: TGOPlayer, target_user: TGOPlayer,  image_factory, original_view=None):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.target_user = target_user
        self.image_factory = image_factory
        self.original_view = original_view

        self.interaction_lock = asyncio.Lock()


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_view_items()
        self.rebuild_view()
    def update_view_items(self):
        # update labels
        # update disabled state
        # update styles
        pass

    def rebuild_view(self):
        self.clear_items()

        # add items to view
