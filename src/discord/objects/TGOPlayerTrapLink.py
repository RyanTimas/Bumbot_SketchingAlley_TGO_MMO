import os

from PIL import Image
from src.discord.handlers.ItemUnlockHandler.ItemUnlockImageFactory import ItemUnlockImageFactory
from src.discord.objects import TGOPlayerItem
from src.discord.objects.CreatureRarity import CreatureRarity
from src.resources.constants.file_paths import ITEM_BASE, IMAGE_FILE_EXTENSION


class TGOPlayerTrapLink:
    def __init__(self,
         player_id: int, active_trap:TGOPlayerItem,
         active_trap_mode:str,
         player_trap_charges:int, player_max_trap_charges:int,
         trap_scheduled_start_time:int, trap_scheduled_mode_end_time:int
    ):
        self.player_id = player_id
        self.active_trap = active_trap

        self.active_trap_mode = active_trap_mode

        self.player_trap_charges = player_trap_charges
        self.player_max_trap_charges = player_max_trap_charges

        self.trap_scheduled_start_time = trap_scheduled_start_time
        self.trap_scheduled_mode_end_time = trap_scheduled_mode_end_time