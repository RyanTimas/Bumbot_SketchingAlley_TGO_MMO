from typing import Optional, Dict, Any

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler, get_user_db_handler
from src.discord.game_features.creature_enounter.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.objects.CreatureRarity import MYTHICAL
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.discord.objects import TGOPlayer

def catch_creature(user_id: int, creature: TGOCreature, environment: TGOEnvironment, spawn_user: Optional[TGOPlayer] = None, is_afk_catch = False) -> Dict[str, Any]:
    # Ensure we have a user profile object (for display name / nickname)
    catch_user = get_tgommo_db_handler().get_user_profile_by_user_id(user_id, convert_to_object=True)

    # Generate embed/image/total_xp (CreatureEmbedHandler currently returns these synchronously)
    embed_handler = CreatureEmbedHandler(creature=creature, environment=environment, spawn_user=spawn_user)
    successful_catch_embed, successful_catch_image, total_xp = embed_handler.generate_catch_embed(catch_user=catch_user, is_afk_catch=is_afk_catch)

    # insert record of user catching the creature & give user xp for catching the creature
    catch_id = get_tgommo_db_handler().insert_new_user_creature(params=(user_id, creature.creature_id, creature.variant_no, creature.environment_id, creature.local_rarity == MYTHICAL))
    get_user_db_handler().update_xp(total_xp, user_id, catch_user.nickname)

    # Optionally run avatar unlock checks (UI callers can await these if they are async; keep them here for shared logic)
    # Note: these are async in your codebase; callers should call them as needed.
    return {
        "catch_id": catch_id,
        "catch_embed": successful_catch_embed,
        "catch_image": successful_catch_image,
        "total_xp": total_xp,
        "user_profile": catch_user,
        "embed_handler": embed_handler,
    }