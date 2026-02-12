import asyncio
import discord

from src.commons.CommonViewComponents import create_go_back_button, create_close_button
from src.discord.objects.TGOPlayer import TGOPlayer


class BaseView(discord.ui.View):
    def __init__(self, message_author: TGOPlayer, target_user: TGOPlayer,  image_factory=None, original_view=None):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.target_user = target_user
        self.image_factory = image_factory
        self.original_view = original_view

        self.page_num = 1

        self.interaction_lock = asyncio.Lock()

        # BUTTONS
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=4, interaction_lock=self.interaction_lock, message_author_id=self.message_author.user_id)
        self.close_button = create_close_button(row=4, interaction_lock=self.interaction_lock, message_author_id=self.message_author.user_id)


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

        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)