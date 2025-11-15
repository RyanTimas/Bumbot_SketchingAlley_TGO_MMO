from src.discord.objects.CreatureRarity import CreatureRarity


class TGOPlayerItem:
    def __init__(self, item_num:int, item_id: int, item_name: str, item_type: str, item_description: str, rarity:CreatureRarity, is_rewardable: bool, img_root: str, default_uses: int):
        self.item_num = item_num
        self.item_id = item_id
        self.item_name = item_name

        self.item_type = item_type
        self.item_description = item_description

        self.rarity = rarity
        self.is_rewardable = is_rewardable
        self.img_root = img_root
        self.default_uses = default_uses