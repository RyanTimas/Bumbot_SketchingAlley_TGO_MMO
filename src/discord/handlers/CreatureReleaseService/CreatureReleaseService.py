# src/discord/game_features/creature_inventory/CreatureReleaseService.py
import discord

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.handlers.CreatureReleaseService.CreatureReleaseRewardHandler import CreatureReleaseRewardHandler
from src.discord.handlers.CreatureReleaseService.ReleaseResultImageFactory import ReleaseResultImageFactory


class CreatureReleaseService:
    @staticmethod
    async def release_creatures_with_rewards(user_id: int, creature_ids: list, interaction: discord.Interaction = None):
        """
        Release creatures and handle rewards calculation/distribution
        Returns: (currency_earned, earned_items)
        """
        # Release creatures from database
        success = get_tgommo_db_handler().update_user_creature_set_is_released(creature_ids=creature_ids)
        if not success:
            return None

        # Calculate and distribute rewards
        reward_handler = CreatureReleaseRewardHandler(user_id)
        currency_earned, earned_items = reward_handler.calculate_rewards(creature_ids)

        # Update user currency and items
        get_tgommo_db_handler().update_user_profile_currency(user_id=user_id, new_currency=currency_earned)
        for item, count in earned_items:
            get_tgommo_db_handler().update_user_profile_available_items(
                user_id=user_id,
                item_id=item.item_id,
                new_amount=count
            )

        return currency_earned, earned_items

    @staticmethod
    def create_release_results_file(user, currency_earned: int, earned_items: list, count_released: int):
        """Create release results image file"""
        release_result_factory = ReleaseResultImageFactory(user=user)
        release_results_image = release_result_factory.get_creature_inventory_page_image(
            currency=currency_earned,
            earned_items=earned_items,
            count_released=count_released
        )
        return convert_to_png(release_results_image, 'release_results.png')