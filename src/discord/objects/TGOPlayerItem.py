from src.discord.objects.CreatureRarity import CreatureRarity
from src.discord.objects.TGOAvatar import TGOAvatar


class TGOPlayerItem:
    def __init__(self, inventory_id: int, item_name: str, item_type: str, item_description: str, is_rewardable: bool, rarity: CreatureRarity):
        self.inventory_id = inventory_id
        self.item_name = item_name

        self.item_type = item_type
        self.item_description = item_description
        self.is_rewardable = is_rewardable
        self.rarity = rarity