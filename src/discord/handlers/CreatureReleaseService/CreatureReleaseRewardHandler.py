import math
import random

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.CreatureRarity import get_rarity_hierarchy_value
from src.resources.constants.TGO_MMO_constants import *


class CreatureReleaseRewardHandler:
    def __init__(self, user_id):
        self.user_id = user_id
        self.rewardable_items = get_tgommo_db_handler().get_rewardable_inventory_items(convert_to_object=True)


    def calculate_rewards(self, selected_creature_ids):
        currency_earned = self.calculate_currency_amount(released_creature_total = len(selected_creature_ids))
        earned_items = self.get_earned_items(selected_creature_ids)
        return currency_earned, earned_items


    def calculate_currency_amount(self, released_creature_total):
        total_currency = 0
        for _ in range(0, released_creature_total):
            total_currency += random.randint(1, 5)
        return total_currency


    def get_earned_items(self, selected_creature_ids):
        # start with any milestone items
        earned_items = self.get_release_milestone_items()

        # for each released creature, roll for random items
        for selected_id in selected_creature_ids:
            creature = get_tgommo_db_handler().get_user_creature_by_catch_id(selected_id, convert_to_object=True)
            earned_items.extend(self.get_random_items(creature= creature))
            # todo: roll for default items
        return self.convert_items_to_count_map(earned_items)

    def get_random_items(self, creature):
        rarity_item_drop_rates = {
            TGOMMO_RARITY_COMMON: 15,
            TGOMMO_RARITY_UNCOMMON: 25,
            TGOMMO_RARITY_NORMAL: 25,
            TGOMMO_RARITY_RARE: 10,
            TGOMMO_RARITY_EPIC: 10,
            TGOMMO_RARITY_LEGENDARY: 5,
            TGOMMO_RARITY_MYTHICAL: 1,
            TGOMMO_RARITY_TRANSCENDANT: 1,
            TGOMMO_RARITY_OMNIPOTENT: 1
        }

        if random.randint(1, rarity_item_drop_rates[creature.local_rarity.name]) == 1:
            if creature.local_rarity.name == TGOMMO_RARITY_MYTHICAL:

                # guaranteed drops for mythical creatures - Legendary Bait OR Epic Bait, Rare Charm
                bait_type_id = ITEM_ID_LEGENDARY_BAIT if random.randint(1,5) == 1 else ITEM_ID_EPIC_BAIT
                return [
                    get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=bait_type_id, convert_to_object=True),
                    get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=ITEM_ID_RARE_CHARM, convert_to_object=True),
                ]
            if creature.local_rarity.name == TGOMMO_RARITY_TRANSCENDANT:
                # guaranteed drops for mythical creatures - Mythical Bait, Legendary Bait, Epic Charm
                return [
                    get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=ITEM_ID_MYTHICAL_BAIT, convert_to_object=True),
                    get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=ITEM_ID_LEGENDARY_BAIT, convert_to_object=True),
                    get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=ITEM_ID_EPIC_CHARM, convert_to_object=True),
                ]

            earned_item = self.roll_for_random_item(creature)
            return [earned_item,]
        return []
    def roll_for_random_item(self, creature):
        reward_pool = []
        creature_rarity_hierarchy_value = get_rarity_hierarchy_value(creature.local_rarity.name)

        rarity_bonuses_rates = {
            TGOMMO_RARITY_COMMON: 25,
            TGOMMO_RARITY_UNCOMMON: 25,
            TGOMMO_RARITY_NORMAL: 15,
            TGOMMO_RARITY_EPIC: 10,
            TGOMMO_RARITY_RARE: 10,
            TGOMMO_RARITY_LEGENDARY: 7,
            TGOMMO_RARITY_MYTHICAL: 5,
            TGOMMO_RARITY_TRANSCENDANT: 1,
            TGOMMO_RARITY_OMNIPOTENT: 1
        }

        for item in self.rewardable_items:
            # only throw items at or above the creature's rarity into the pool
            if item.item_type in (ITEM_TYPE_BAIT, ITEM_TYPE_CHARM):
                item_rarity_level = get_rarity_hierarchy_value(item.rarity.name)

                if item_rarity_level >= creature_rarity_hierarchy_value:
                    rate = 1 * rarity_bonuses_rates[item.rarity.name] * (.1 if item.item_type == ITEM_TYPE_CHARM else 1)

                    # perform rarity matching bonus
                    if creature.local_rarity.name == item.rarity.name:
                        rate = 50

                    reward_pool.extend([item] * math.floor(rate))
        return reward_pool[random.randint(0, len(reward_pool) -1)]

    def get_release_milestone_items(self):
        milestone_amounts = {
            TGOMMO_RARITY_COMMON: 10,
            TGOMMO_RARITY_UNCOMMON: 25,
            TGOMMO_RARITY_RARE: 50,
            TGOMMO_RARITY_EPIC: 100,
            TGOMMO_RARITY_LEGENDARY: 250,
            TGOMMO_RARITY_MYTHICAL: 500,
        }

        user_released_creature_amount = len(get_tgommo_db_handler().get_item_collection_by_user_id(user_id=self.user_id, convert_to_object=True))
        milestone_items = []

        # if user has not released any creatures yet, give them a starter pack of 5 bait, 1 legendary bait, and 1 charm
        if not get_tgommo_db_handler().get_item_collection_by_user_id(user_id=self.user_id, convert_to_object=True):
            milestone_item_bait = get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=ITEM_ID_BAIT, convert_to_object=True)

            milestone_items.extend([milestone_item_bait] * 5)
            milestone_items.append(get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=ITEM_ID_LEGENDARY_BAIT, convert_to_object=True))
            milestone_items.append(get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=ITEM_ID_CHARM, convert_to_object=True))

        for rarity, milestone in milestone_amounts.items():
            if user_released_creature_amount % milestone == 0 and user_released_creature_amount > 0:
                # Find items of this rarity from rewardable items
                rarity_items = [item for item in self.rewardable_items if item.rarity.name == rarity]
                if rarity_items:
                    # Add a random item of this rarity
                    milestone_items.append(random.choice(rarity_items))
        return milestone_items


    def convert_items_to_count_map(self, earned_items):
        # Convert to list of tuples (item, count)
        item_counts = {}
        for item in earned_items:
            item_counts[item] = (item_counts[item] + 1) if item in item_counts else 1
        return [(item, count) for item, count in item_counts.items()]