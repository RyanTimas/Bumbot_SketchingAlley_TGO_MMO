from src.resources.constants.TGO_MMO_constants import SUB_ENVIRONMENT_RIVER


class EnvironmentCreatureLink:
    def __init__(self, creature_dex_no, creature_variant_no, environment_dex_no, spawn_time, local_rarity, local_name="", sub_environment=SUB_ENVIRONMENT_RIVER, local_img_root="", local_dex_no=0, local_variant_no=0):
        self.creature_dex_no = creature_dex_no
        self.creature_variant_no = creature_variant_no

        self.environment_dex_no = environment_dex_no
        self.spawn_time = spawn_time

        self.local_rarity = local_rarity
        self.local_name = local_name
        self.sub_environment = sub_environment
        self.local_img_root = local_img_root
        self.local_dex_no = local_dex_no
        self.local_variant_no = local_variant_no
