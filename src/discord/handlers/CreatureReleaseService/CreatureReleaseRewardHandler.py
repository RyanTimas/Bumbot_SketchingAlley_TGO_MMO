import math
import random
import traceback

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.CreatureRarity import get_rarity_hierarchy_value
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.TGO_MMO_creature_constants import MUSSEL_DEX_NO

class CreatureReleaseRewardHandler:
    def __init__(self, user_id):
        self.user_id = user_id
        self.rewardable_items = get_tgommo_db_handler().get_rewardable_inventory_items()
        self._item_cache = {}

    def get_release_rewards(self, selected_creature_ids):
        currency_earned = self.calculate_earned_currency(len(selected_creature_ids))
        earned_items = self._get_earned_items(selected_creature_ids)
        return currency_earned, earned_items

    def _get_earned_items(self, selected_creature_ids):
        earned_items = self.get_milestone_rewards(len(selected_creature_ids))

        for creature in get_tgommo_db_handler().get_user_creatures_by_catch_ids(selected_creature_ids):
            # Check for creature-specific rewards first
            earned_items.extend(self.get_creature_specific_rewards(creature))
            # Roll for random rewards based on creature rarity and item pool
            earned_items.extend(self.get_random_items_for_creature(creature))

        return self._convert_items_to_count_map(earned_items)

    def _convert_items_to_count_map(self, earned_items):
        item_counts = {}
        for item in earned_items:
            item_counts[item] = item_counts.get(item, 0) + 1
        return [(item, count) for item, count in item_counts.items()]

    # region reward currency methods
    def calculate_earned_currency(self, creature_count):
        if creature_count <= 0:
            return 0
        return sum(random.randint(*RewardConfig.CURRENCY_RANGE) for _ in range(creature_count))
    # endregion

    # region item drop methods
    def _get_item_by_id(self, item_id):
        if item_id not in self._item_cache:
            self._item_cache[item_id] = get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=item_id, convert_to_object=True)
        return self._item_cache[item_id]

    def get_random_items_for_creature(self, creature):
        earned_items = []

        # Then check for regular rarity-based drops
        if random.randint(1, RewardConfig.RARITY_DROP_RATES[creature.local_rarity.name]) == 1:
            if creature.local_rarity.name == TGOMMO_RARITY_MYTHICAL:
                earned_items.extend(self._get_mythical_guaranteed_drops())
            elif creature.local_rarity.name == TGOMMO_RARITY_TRANSCENDANT:
                earned_items.extend(self._get_transcendant_guaranteed_drops())
            else:
                earned_item = self._roll_for_random_item(creature)
                if earned_item:
                    earned_items.append(earned_item)

        return earned_items

    def get_creature_specific_rewards(self, creature):
        """Get rewards specific to the creature's dex number."""
        if creature.dex_no not in RewardConfig.CREATURE_SPECIFIC_REWARDS:
            return []

        reward_config = RewardConfig.CREATURE_SPECIFIC_REWARDS[creature.dex_no]

        # Check if reward should be given based on chance
        if random.randint(1, 100) > reward_config['chance']:
            return []

        # Handle weighted item drops
        if 'weighted_items' in reward_config:
            return [self._roll_weighted_item(reward_config['weighted_items'])]

        # Fallback to item_types method for other creatures
        if 'item_types' in reward_config and reward_config['item_types']:
            matching_items = [
                item for item in self.rewardable_items
                if item.item_type in reward_config['item_types']
            ]
            return [random.choice(matching_items)] if matching_items else []

        return []

    def _roll_weighted_item(self, weighted_items):
        weighted_pool = []
        for item_id, weight in weighted_items.items():
            item = self._get_item_by_id(item_id)
            weighted_pool.extend([item] * weight)

        return random.choice(weighted_pool) if weighted_pool else None

    def _get_mythical_guaranteed_drops(self):
        bait_type_id = (ITEM_ID_LEGENDARY_BAIT if random.randint(1, RewardConfig.LEGENDARY_BAIT_CHANCE) == 1 else ITEM_ID_EPIC_BAIT)
        return [self._get_item_by_id(bait_type_id), self._get_item_by_id(ITEM_ID_RARE_CHARM)]

    def _get_transcendant_guaranteed_drops(self):
        return [self._get_item_by_id(ITEM_ID_MYTHICAL_BAIT), self._get_item_by_id(ITEM_ID_LEGENDARY_BAIT), self._get_item_by_id(ITEM_ID_EPIC_CHARM)]

    def _roll_for_random_item(self, creature):
        reward_pool = []
        creature_rarity_hierarchy_value = get_rarity_hierarchy_value(creature.local_rarity.name)

        for item in self.rewardable_items:
            if item.item_type in (ITEM_TYPE_BAIT, ITEM_TYPE_CHARM):
                item_rarity_level = get_rarity_hierarchy_value(item.rarity.name)

                if item_rarity_level >= creature_rarity_hierarchy_value:
                    rate = (1 * RewardConfig.RARITY_BONUS_RATES[item.rarity.name] *
                           (RewardConfig.CHARM_RATE_MULTIPLIER if item.item_type == ITEM_TYPE_CHARM else 1))

                    if creature.local_rarity.name == item.rarity.name:
                        rate = RewardConfig.RARITY_MATCH_BONUS_RATE

                    reward_pool.extend([item] * math.floor(rate))

        if not reward_pool:
            return None
        return reward_pool[random.randint(0, len(reward_pool) - 1)]
    # endregion

    # region milestone methods
    def get_milestone_rewards(self, selected_creatures_count=0):
        user_released_creature_amount = len(get_tgommo_db_handler().get_user_creatures_by_user_id(user_id=self.user_id, is_released=True, convert_to_object=True))
        milestone_items = []

        # Add a starter pack if this is the user's first time releasing creatures (no released creatures in DB yet)
        if not get_tgommo_db_handler().get_inventory_item_collection_by_user_id(user_id=self.user_id, convert_to_object=True):
            milestone_items.extend(self._get_starter_pack())

        # Check milestones
        milestone_items.extend(self._check_milestone_thresholds(user_released_creature_amount, selected_creatures_count))

        return milestone_items

    def _get_starter_pack(self):
        milestone_item_bait = self._get_item_by_id(ITEM_ID_BAIT)
        return [milestone_item_bait] * RewardConfig.STARTER_BAIT_COUNT + [self._get_item_by_id(ITEM_ID_LEGENDARY_BAIT), self._get_item_by_id(ITEM_ID_CHARM)]

    def _check_milestone_thresholds(self, release_count_total, new_release_count):
        milestone_items = []
        old_release_count = release_count_total - new_release_count

        for rarity, milestone_threshold in RewardConfig.MILESTONE_AMOUNTS.items():
            # Calculate how many milestones the user had before and after
            old_milestones = old_release_count // milestone_threshold
            new_milestones = release_count_total // milestone_threshold
            print(f"Checking milestones for rarity {rarity}: old_release_count={old_release_count}, new_release_count={new_release_count}, old_milestones={old_milestones}, new_milestones={new_milestones}")

            # Number of new milestones crossed
            milestones_earned = new_milestones - old_milestones

            if milestones_earned > 0:
                rarity_items = [item for item in self.rewardable_items if item.rarity.name == rarity]
                if rarity_items:
                    # Give one item for each milestone crossed
                    for _ in range(milestones_earned):
                        milestone_items.append(random.choice(rarity_items))

        return milestone_items    # endregion

class RewardConfig:
    CURRENCY_RANGE = (1, 5)

    RARITY_DROP_RATES = {
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
    RARITY_BONUS_RATES = {
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
    MILESTONE_AMOUNTS = {
        TGOMMO_RARITY_COMMON: 10,
        TGOMMO_RARITY_UNCOMMON: 25,
        TGOMMO_RARITY_RARE: 50,
        TGOMMO_RARITY_EPIC: 100,
        TGOMMO_RARITY_LEGENDARY: 250,
        TGOMMO_RARITY_MYTHICAL: 500,
    }
    CREATURE_SPECIFIC_REWARDS = {
        # 100% chance to get a pearl item if mussel is caught
        MUSSEL_DEX_NO: {
            'item_types': ITEM_TYPE_PEARL,
            'chance': 100,  # 100% chance to get a pearl
            'weighted_items': {
                ITEM_ID_WHITE_PEARL: 50,
                ITEM_ID_PINK_PEARL: 25,
                ITEM_ID_GREEN_PEARL: 15,
                ITEM_ID_PETROL_PEARL: 10,
                ITEM_ID_PURPLE_PEARL: 8,
                ITEM_ID_GOLD_PEARL: 6,
                ITEM_ID_BLACK_PEARL: 5,
            }
        }
    }

    LEGENDARY_BAIT_CHANCE = 5
    RARITY_MATCH_BONUS_RATE = 50
    CHARM_RATE_MULTIPLIER = 0.1
    STARTER_BAIT_COUNT = 5