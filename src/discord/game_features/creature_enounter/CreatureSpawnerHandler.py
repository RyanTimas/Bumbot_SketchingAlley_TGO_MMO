import asyncio
import datetime
import ssl
import threading
import time
import traceback
from copy import deepcopy
from datetime import datetime, timezone

import pytz
from PIL import Image
from discord.ext.commands import Bot
from sqlalchemy.util import await_only

from src.commons.CommonFunctions import flip_coin, convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_enounter.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.game_features.creature_enounter.CreatureEncounterView import CreatureEncounterView
from src.discord.objects import TGOPlayer
from src.discord.objects.CreatureRarity import *
from src.discord.objects.CreatureSpawnBonus import CreatureSpawnBonus
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *
from src.resources.constants.general_constants import TGOMMO_ROLE, TGOMMO_CREATURE_SPAWN_CHANNEL_ID


class CreatureSpawnerHandler:
    def __init__(self, discord_bot: Bot):
        self.discord_bot = discord_bot
        self.are_creatures_spawning = True

        self.current_environment = None
        self.creature_spawn_pool = None
        self.last_spawn_time = None
        self.is_day = None
        self.time_of_day = None

        self.active_bonuses = []

        self.pending_environment = None
        self.environment_change_checked_for_today = False

        self.define_time_of_day()
        self.define_environment_and_spawn_pool(environment_dex_no=2, environment_variant_no=1 if self.is_day else 2)

        self.spawn_event = asyncio.Event()
        self._spawner_running = False


    '''FUNCTIONS TO INITIALIZE SPAWNER DATA'''
    def define_time_of_day(self):
        timezone = self.current_environment.timezone if self.current_environment else BASE_TIMEZONE
        dawn_timestamp_1 = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 6, 59, 0).astimezone(timezone)
        dawn_timestamp_2 = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 7, 59, 0).astimezone(timezone)
        day_timestamp = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 8, 59, 0).astimezone(timezone)
        dusk_timestamp_1 = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 18, 59, 0).astimezone(timezone)
        dusk_timestamp_2 = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 19, 59, 0).astimezone(timezone)
        night_timestamp = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 20, 59, 0).astimezone(timezone)

        current_time = datetime.datetime.now(pytz.UTC).astimezone(timezone)

        self.last_spawn_time = current_time
        self.is_day = (7 <= current_time.hour < 19)

        if current_time.hour in (6, 7, 18, 19):
            self.time_of_day = DAWN if current_time.hour in (6, 7) else DUSK
        else:
            self.time_of_day = DAY if self.is_day else NIGHT

    def define_environment_and_spawn_pool(self, current_environment = None, environment_dex_no: int = 0, environment_variant_no: int = 0):
        if not current_environment:
            self.current_environment  = get_tgommo_db_handler().get_environment_by_dex_no_and_variant_no(dex_no=environment_dex_no, variant_no=environment_variant_no)
        self.creature_spawn_pool = get_tgommo_db_handler().get_creatures_for_environment_by_environment_id(environment_id=self.current_environment.environment_id)
        if IS_EVENT:
            self.creature_spawn_pool = get_tgommo_db_handler().get_event_creatures_from_environment(convert_to_object=True)

    '''FUNCTIONS TO HANDLE SPAWNER BEHAVIOR'''
    # kicks off the creature spawner
    def start_creature_spawner(self):
        if not self._spawner_running:
            asyncio.create_task(self._creature_spawner())

    # Toggles whether creatures are spawning or not
    def toggle_creature_spawner(self, ctx):
        self.are_creatures_spawning = not self.are_creatures_spawning
        return "creatures are now spawning" if self.are_creatures_spawning else "creatures are no longer spawning"

    # Main loop that determines when to spawn creatures at random intervals
    async def _creature_spawner(self):
        if self._spawner_running:
            return  # Prevent multiple spawners

        self._spawner_running = True

        try:
            while self.are_creatures_spawning:

                try:
                    await self.spawn_creature()
                except (ssl.SSLError, Exception) as e:
                    # Handle all errors in a single block
                    error_type = "SSL Error" if isinstance(e, ssl.SSLError) else "Error"
                    print(f"{error_type} occurred during creature spawning- skipping to next creature - {e}")
                    traceback.print_exc()
                    await asyncio.sleep(5)

                # wait between 3 and 5 minutes before spawning another creature - will spawn 288 - 480 creatures a day
                normal_charm_active = any(bonus.bonus_type == f'{ITEM_TYPE_CHARM}{TGOMMO_RARITY_NORMAL}' for bonus in self.active_bonuses)

                min_spawn_interval = 1 if normal_charm_active else 3
                max_spawn_interval = 3 if normal_charm_active else 5

                # check if a new day has begun or if a day/night transition has occurred or if environment needs to change
                await self.handle_post_spawn_events()

                # cooldown for the next creature spawn
                sleep_duration = random.uniform(min_spawn_interval, max_spawn_interval) * 60
                try:
                    await asyncio.wait_for(self.spawn_event.wait(), timeout=sleep_duration)
                    self.spawn_event.clear()  # Reset the event for next time
                except asyncio.TimeoutError:
                    pass  # Normal timeout, continue spawning
        finally:
            self._spawner_running = False


    '''FUNCTIONS TO HANDLE CREATURE SPAWNING LOGIC'''
    # Spawns a creature and sends a message to the discord channel
    async def spawn_creature(self, creature: TGOCreature = None, user: TGOPlayer = None, rarity = None):
        creature = creature if creature else await self.creature_picker(rarity= rarity)
        creature_embed, creature_thumb_img, creature_encounter_img = CreatureEmbedHandler(creature=creature, environment=self.current_environment, time_of_day=self.time_of_day, spawn_user=user, active_bonuses=self.active_bonuses).generate_spawn_embed()

        spawn_message = await self.discord_bot.get_channel(TGOMMO_CREATURE_SPAWN_CHANNEL_ID).send(
            content=TGOMMO_ROLE,
            view= CreatureEncounterView(discord_bot=self.discord_bot, creature=creature, environment=self.current_environment, spawn_user=user),
            files=[creature_thumb_img, creature_encounter_img],
            embed=creature_embed
        )

        # Create separate task for despawn
        if creature.local_rarity.name != TRANSCENDANT.name and creature.local_rarity.name != MYTHICAL.name:
            thread = threading.Thread(target=self._handle_despawn, args=(creature, spawn_message))
            thread.daemon = True
            thread.start()

        # see if duplicate creatures should spawn for swarm effect, swarms are not eligible for bait spawns
        if not user:
            await self.duplicate_creature_spawner(creature=creature)

    # Spawns a duplicate creature to give illusion of a swarm
    async def duplicate_creature_spawner(self, creature: TGOCreature):
        critter_chain_multiplier = 1

        # 12% chance to spawn a duplicate
        spawn_duplicate = flip_coin(total_iterations=3) and creature.local_rarity.name in (COMMON.name, UNCOMMON.name, RARE.name)
        while spawn_duplicate:
            # 6% chance to spawn more duplicates
            duplicate_creature = deepcopy(creature)

            critter_chain_multiplier += 1
            if random.randint(1, ((MYTHICAL_SPAWN_CHANCE*2) // critter_chain_multiplier)) == 1:
                duplicate_creature.set_creature_rarity(MYTHICAL)

            await self.spawn_creature(duplicate_creature)

            # 6% chance to spawn more duplicates
            spawn_duplicate = flip_coin(total_iterations=4)
        return

    # Picks a random creature from the spawn pool
    async def creature_picker(self, rarity= None):
        rarity = rarity if rarity else self.get_creature_rarity()

        available_creatures = [creature for creature in self.creature_spawn_pool if creature.local_rarity.name == rarity.name]
        selected_index = random.randint(0, len(available_creatures)-1) if len(available_creatures) > 1 else 0

        selected_creature = deepcopy(available_creatures[selected_index])

        # Check if mythical spawn occurs
        mythical_odds = MYTHICAL_SPAWN_CHANCE // (2 if any(bonus.bonus_type == F'{ITEM_TYPE_CHARM}{TGOMMO_RARITY_MYTHICAL}' for bonus in self.active_bonuses) else 1)
        if rarity.name != TRANSCENDANT.name and random.randint(0, mythical_odds) == 1:
            selected_creature.set_creature_rarity(MYTHICAL)

        selected_creature.refresh_spawn_and_despawn_time(timezone=self.current_environment.timezone, minute_offset=720 if (rarity.name == MYTHICAL.name or rarity.name == TRANSCENDANT.name) else 0)
        return selected_creature

    # Determines the rarity of the creature to spawn based on active bonuses and time of day
    def get_creature_rarity(self):
        # 1/8192 chance to spawn transcendant
        if flip_coin(total_iterations= 7 if IS_EVENT else 13):
            return TRANSCENDANT

        bonus = next((bonus for bonus in self.active_bonuses if bonus.bonus_type == ITEM_TYPE_CHARM and bonus.local_rarity.name not in [TGOMMO_RARITY_NORMAL, TGOMMO_RARITY_MYTHICAL]), None)

        # IF DUSK OR DAWN, INCREASE CHANCE OF NORMAL RARITY ROLL
        is_dawn_or_dusk = self.time_of_day in (DUSK, DAWN)

        if bonus and random.randint(1, bonus.spawn_odds // (2 if is_dawn_or_dusk else 1)) == 1:
            return bonus.rarity
        return get_rarity() if (random.randint(1, 3) == 1 or is_dawn_or_dusk) else COMMON

    # Handles despawning of a creature after its despawn time has elapsed
    def _handle_despawn(self, creature: TGOCreature, spawn_message):
        time.sleep(creature.time_to_despawn)
        try:
            # Try to fetch the message to check if it still exists
            channel = self.discord_bot.get_channel(spawn_message.channel.id)
            asyncio.run_coroutine_threadsafe(channel.fetch_message(spawn_message.id), self.discord_bot.loop).result()
        except discord.NotFound:
            return

        creature_embed = CreatureEmbedHandler(creature=creature, environment=self.current_environment).generate_despawn_embed()
        asyncio.run_coroutine_threadsafe(spawn_message.delete(), self.discord_bot.loop)
        asyncio.run_coroutine_threadsafe(
            self.discord_bot.get_channel(TGOMMO_CREATURE_SPAWN_CHANNEL_ID).send(
                files=[creature_embed[1]],
                embed=creature_embed[0]
            ), self.discord_bot.loop
        )


    '''FUNCTIONS TO HANDLE ADDING / REMOVING SPAWN BONUSES'''
    def add_spawn_bonus(self, bonus_type: str, bonus_name:str, rarity: str, image):
        spawn_ceiling_rate = {
            TGOMMO_RARITY_NORMAL: 0,
            TGOMMO_RARITY_MYTHICAL: 0,

            TGOMMO_RARITY_COMMON: 1,
            TGOMMO_RARITY_UNCOMMON: 2,
            TGOMMO_RARITY_RARE: 4,
            TGOMMO_RARITY_EPIC: 8,
            TGOMMO_RARITY_LEGENDARY: 16,
        }

        if not any(bonus.bonus_type == bonus_type for bonus in self.active_bonuses):
            self.active_bonuses.append(
                CreatureSpawnBonus(
                    bonus_type=bonus_type,
                    bonus_name=bonus_name,
                    rarity=get_rarity_by_name(rarity),
                    spawn_odds=spawn_ceiling_rate[rarity],
                    image=image
                )
            )

            # Interrupt current sleep to apply new bonus immediately
            self.spawn_event.set()

            return True
        return False

    def remove_spawn_bonus(self, bonus_type: str, ):
        self.active_bonuses = [bonus for bonus in self.active_bonuses if not (bonus.bonus_type == bonus_type)]


    '''FUNCTIONS TO HANDLE TIME / ENVIRONMENT / CREATURE POOL CHANGES'''
    async def handle_post_spawn_events(self):
        current_time = datetime.datetime.now(pytz.UTC).astimezone(self.current_environment.timezone)

        self._handle_day_night_cycle(current_time=current_time)
        await self._handle_environment_change_cycle(current_time=current_time)

        self._handle_time_based_resets(current_time=current_time)

    # Handles hourly and daily resets
    def _handle_time_based_resets(self, current_time: datetime.datetime = None):
        # Clear user catches if the hour has changed
        if current_time.hour != self.last_spawn_time.hour:
            USER_CATCHES_HOURLY.clear()

        # Clear daily user catches if a new day has begun & reset environment change check
        if current_time.date() > self.last_spawn_time.date():
            USER_CATCHES_DAILY.clear()
            self.environment_change_checked_for_today = False

        self.last_spawn_time = current_time

    # Checks if a new day has begun or if a day/night transition has occurred, and if so, reloads the environment and spawn pool
    def _handle_day_night_cycle(self, current_time: datetime.datetime = None):
        old_time_of_day = 'day' if 7 <= self.last_spawn_time.hour < 19 else 'night'
        new_time_of_day = 'day' if 7 <= current_time.hour < 19 else 'night'
        is_day_night_transition = old_time_of_day != new_time_of_day

        if current_time.hour in (6, 7, 18, 19):
            self.time_of_day = DAWN if current_time.hour in (6, 7) else DUSK
        else:
            self.time_of_day = DAY if self.is_day else NIGHT

        if is_day_night_transition:
            self.is_day = not self.is_day
            self.define_environment_and_spawn_pool(current_environment=self.current_environment,)

        self.last_spawn_time = current_time

    # Checks if the environment should change today, schedules the change for noon
    async def _handle_environment_change_cycle(self, current_time: datetime.datetime = None):
        environment_change_check_time = 11

        # Check for environment change at 11 am
        if current_time.hour == environment_change_check_time and not self.environment_change_checked_for_today:
            self.environment_change_checked_for_today = True

            # Decide if we are staying in the same environment or switching, 50/50 chance
            should_change_environment = flip_coin(total_iterations=1)
            if not should_change_environment:
                return

            # If we are changing environments, get a new random environment
            new_environment = get_tgommo_db_handler().get_random_environment_in_rotation(is_night_environment=0 if self.is_day else 1, convert_to_object=True)
            while new_environment.dex_no == self.current_environment.dex_no:
                new_environment = get_tgommo_db_handler().get_random_environment_in_rotation(is_night_environment=0 if self.is_day else 1, convert_to_object=True)
            self.pending_environment = new_environment

            # Schedule environment change for noon today in a separate thread
            threading.Thread(target=self._schedule_environment_change, args=(), daemon=True).start()
            self.environment_changed_today = current_time.date()

            # Announce the environment change in the spawn channel
            await self.discord_bot.get_channel(TGOMMO_CREATURE_SPAWN_CHANNEL_ID).send(
                f"🌍 **Environment Alert!** The environment will change to **{new_environment.name}** at noon!",
                files=[convert_to_png(Image.open(f"{TGOMMO_TRAVEL_ADVISORY_BASE}{new_environment.dex_no}{IMAGE_FILE_EXTENSION}"), file_name=f"travel_advisory_image.png"), ]
            )
    def _schedule_environment_change(self):
        current_time = datetime.datetime.now(self.pending_environment.timezone).astimezone(self.current_environment.timezone)
        environment_change_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)

        # Calculate seconds until environment change
        time_until_environment_change = (environment_change_time - current_time).total_seconds()

        # Sleep until environment change
        time.sleep(time_until_environment_change)

        # Execute environment change
        if hasattr(self, 'pending_environment') and self.pending_environment:
            self.current_environment = self.pending_environment

            # Reset spawn pool with the new environment
            self.define_environment_and_spawn_pool(current_environment=self.current_environment)

            # Send message to channel about environment change
            asyncio.run_coroutine_threadsafe(
                self.discord_bot.get_channel(TGOMMO_CREATURE_SPAWN_CHANNEL_ID).send(
                    f"🌍 **Environment Changed!** Now exploring **{self.current_environment.name}**!",
                    files=[convert_to_png(Image.open(f"{TGOMMO_TRAVEL_ADVISORY_LANDING_BASE}{self.current_environment.dex_no}{IMAGE_FILE_EXTENSION}"), file_name=f"travel_advisory_image.png")]
                ), self.discord_bot.loop
            )

            # Clear the pending environment
            self.pending_environment = None

            # Interrupt current sleep to apply new environment immediately
            self.spawn_event.set()