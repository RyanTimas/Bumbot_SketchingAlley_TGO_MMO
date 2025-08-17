import random


class TGOCreature:
    def __init__(self, name:str, img_path: str, rarity: str):
        self.name = name
        self.img_path = img_path
        self.thumbnail_path = img_path + "_THUMB"
        self.rarity = rarity
        self.despawn_time = random.randint(1, 15)