from discord import Message

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.image_factories.DexIconFactory import DexIconFactory
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment


class EncyclopediaImageFactory:
    def __init__(self, creature: TGOCreature, environment: TGOEnvironment, ctx: Message, verbose = False):
        self.creature = creature
        self.environment = environment
        self.ctx = ctx
        self.verbose = verbose


    def generate_encyclopedia_factory(self):
        # generate dex icons
        dex_icons = self.get_dex_icons(user_id= self.ctx.author.id, verbose= self.verbose)


    def get_dex_icons(self, user_id, verbose=False):
        creatures = get_tgommo_db_handler().get_all_creatures_caught_by_user(user_id=user_id)
        imgs = []

        for creature in creatures:
            creature_name = creature[1]
            variant_name = creature[2]
            dex_no = creature[3]
            variant_no = creature[4]
            rarity = get_tgommo_db_handler().get_creature_rarity_for_environment(creature_id=creature[0], environment_id=1)
            total_catches = creature[5]
            total_mythical_catches = creature[6]

            creature_is_locked = False if total_catches > 0 else True

            dex_icon = DexIconFactory(creature_name=creature_name, dex_no=dex_no, variant_no=variant_no, rarity=rarity, creature_is_locked=creature_is_locked, show_stats=verbose, total_catches=total_catches, total_mythical_catches=total_mythical_catches)
            dex_icon_img = dex_icon.generate_dex_entry_image()

            imgs.append(convert_to_png(dex_icon_img, f'creature_icon_{creature[3]}_{variant_no}.png'))

        return imgs


