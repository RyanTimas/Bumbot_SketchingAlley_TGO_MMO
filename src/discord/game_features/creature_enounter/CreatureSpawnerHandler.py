import asyncio
import ssl
import threading
import time
import traceback
from copy import deepcopy
from datetime import datetime
import datetime
import pytz

from discord.ext.commands import Bot

from src.commons.CommonFunctions import flip_coin
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_enounter.EncounterView import TGOMMOEncounterView
from src.discord.game_features.creature_enounter.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.objects.CreatureRarity import *
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.general_constants import DISCORD_SA_CHANNEL_ID_TGOMMO, TGOMMO_ROLE


class CreatureSpawnerHandler:
    def __init__(self, discord_bot: Bot):
        self.discord_bot = discord_bot

        self.are_creatures_spawning = True

        self.current_environment = None
        self.creature_spawn_pool = None
        self.timezone = None
        self.last_spawn_time = None
        self.is_day = None
        self.time_of_day = None


    # kicks off the creature spawner
    def start_creature_spawner(self):
        self.define_time_of_day()
        self.define_environment_and_spawn_pool(environment_id=1, variant_no=1 if self.is_day else 2)
        asyncio.create_task(self._creature_spawner())


    # Toggles whether creatures are spawning or not
    def toggle_creature_spawner(self, ctx):
        self.are_creatures_spawning = not self.are_creatures_spawning
        return "creatures are now spawning" if self.are_creatures_spawning else "creatures are no longer spawning"


    # Loads a particular environment and defines the spawn pool for that environment
    def define_environment_and_spawn_pool(self, environment_id: int, variant_no: int):
        dex_no = get_tgommo_db_handler().get_environment_by_id(environment_id=environment_id, convert_to_object=True).dex_no
        self.current_environment  = get_tgommo_db_handler().get_environment_by_dex_and_variant_no(dex_no=dex_no, variant_no=variant_no, convert_to_object=True)

        # Retrieve & Define Spawn Pool
        self.creature_spawn_pool = []
        creature_links = get_tgommo_db_handler().get_creatures_from_environment(environment_id=self.current_environment.environment_id)

        for creature_link in creature_links:
            local_name = creature_link[2]
            creature_info = get_tgommo_db_handler().get_creature_by_dex_and_variant_no(dex_no=creature_link[0], variant_no=creature_link[1], convert_to_object=False)

            creature = TGOCreature(creature_id= creature_info[0], name=creature_info[1] if local_name == '' else local_name, variant_name=creature_info[2], dex_no=creature_info[3], variant_no=creature_info[4],full_name=creature_info[5], scientific_name=creature_info[6], kingdom=creature_info[7], description=creature_info[8], img_root=creature_info[9], encounter_rate=creature_info[10], rarity=get_rarity_by_name(creature_link[3]), sub_environment=creature_link[4])
            self.creature_spawn_pool.append(creature)

    def define_time_of_day(self):
        # TODO: WILL PULL TIMEZONE FROM ENVIRONMENT IN FUTURE
        self.timezone = pytz.timezone('US/Eastern')

        dawn_timestamp_1 = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 6, 59, 0).astimezone(self.timezone)
        dawn_timestamp_2 = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 7, 59, 0).astimezone(self.timezone)
        day_timestamp = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 8, 59, 0).astimezone(self.timezone)
        dusk_timestamp_1 = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 18, 59, 0).astimezone(self.timezone)
        dusk_timestamp_2 = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 19, 59, 0).astimezone(self.timezone)
        night_timestamp = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 20, 59, 0).astimezone(self.timezone)

        current_time = datetime.datetime.now(pytz.UTC).astimezone(self.timezone)

        self.last_spawn_time = current_time
        self.is_day = (7 <= current_time.hour < 19)

        if current_time.hour in (6, 7, 18, 19):
            self.time_of_day = DAWN if current_time.hour in (6, 7) else DUSK
        else:
            self.time_of_day = DAY if self.is_day else NIGHT


    # Main loop that determines when to spawn creatures at random intervals
    async def _creature_spawner(self):
        while self.are_creatures_spawning:
            creature = await self.creature_picker()

            try:
                await self.spawn_creature(creature= creature)
                await self.duplicate_creature_spawner(creature=creature)

            except (ssl.SSLError, Exception) as e:
                # Handle all errors in a single block
                error_type = "SSL Error" if isinstance(e, ssl.SSLError) else "Error"
                print(f"{error_type} occurred during creature spawning- skipping to next creature - {e}")
                traceback.print_exc()
                await asyncio.sleep(5)

            # wait between 8 and 12 minutes before spawning another creature - will spawn 288 - 480 creatures a day
            await asyncio.sleep(random.uniform(3, 5) * 60)

            # check if a new day has begun or if a day/night transition has occurred
            self._handle_time_change()


    # Spawns a creature and sends a message to the discord channel
    async def spawn_creature(self, creature: TGOCreature):
        creature_embed = CreatureEmbedHandler(creature=creature, environment=self.current_environment, time_of_day=self.time_of_day).generate_spawn_embed()

        spawn_message = await self.discord_bot.get_channel(DISCORD_SA_CHANNEL_ID_TGOMMO).send(
            content=TGOMMO_ROLE,
            view=TGOMMOEncounterView(discord_bot=self.discord_bot, message=f'Catch', creature=creature, environment=self.current_environment),
            files=[creature_embed[1], creature_embed[2]],
            embed=creature_embed[0]
        )

        # Create separate task for despawn
        if creature.rarity.name != TRANSCENDANT.name and creature.rarity.name != MYTHICAL.name:
            thread = threading.Thread(target=self._handle_despawn, args=(creature, spawn_message))
            thread.daemon = True
            thread.start()

    # Spawns a duplicate creature to give illusion of a swarm
    async def duplicate_creature_spawner(self, creature: TGOCreature):
        critter_chain_multiplier = 1

        # 12% chance to spawn a duplicate
        spawn_duplicate = flip_coin(total_iterations=3) and creature.rarity.name in (COMMON.name, UNCOMMON.name, RARE.name)
        while spawn_duplicate:
            # 6% chance to spawn more duplicates
            duplicate_creature = deepcopy(creature)

            critter_chain_multiplier += 1
            if random.randint(1, ((MYTHICAL_SPAWN_CHANCE*2) // critter_chain_multiplier)) == 1:
                duplicate_creature.rarity = MYTHICAL
                duplicate_creature.img_root += '_S'

            await self.spawn_creature(duplicate_creature)

            # 6% chance to spawn more duplicates
            spawn_duplicate = flip_coin(total_iterations=4)
        return

    # Picks a random creature from the spawn pool
    async def creature_picker(self):
        # FOR LAUNCH, SET COMMON CRITTERS TO BE WAY MORE COMMON BUT MAKE SPAWN MORE FREQUENTLY, only a 25% chance to pull an actual roll
        rarity = get_rarity() if (random.randint(1, 3) == 1 or self.time_of_day in (DUSK, DAWN)) else COMMON
        rarity = TRANSCENDANT if flip_coin(total_iterations=13) else rarity

        available_creatures = [creature for creature in self.creature_spawn_pool if creature.rarity == rarity]
        selected_index = random.randint(0, len(available_creatures)-1) if len(available_creatures) > 1 else 0

        selected_creature = deepcopy(available_creatures[selected_index])

        if rarity.name != TRANSCENDANT.name and random.randint(0, MYTHICAL_SPAWN_CHANCE) == 1:
            selected_creature.rarity = MYTHICAL
            selected_creature.img_root += '_S'

        selected_creature.refresh_spawn_and_despawn_time(timezone=self.timezone, minute_offset=720 if (rarity.name == MYTHICAL.name or rarity.name == TRANSCENDANT.name) else 0)
        return selected_creature

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
            self.discord_bot.get_channel(DISCORD_SA_CHANNEL_ID_TGOMMO).send(
                files=[creature_embed[1]],
                embed=creature_embed[0]
            ), self.discord_bot.loop
        )


    # Checks if a new day has begun or if a day/night transition has occurred, and if so, reloads the environment and spawn pool
    def _handle_time_change(self):
        current_time = datetime.datetime.now(pytz.UTC).astimezone(self.timezone)

        # Clear user catches if the hour has changed
        if current_time.hour != self.last_spawn_time.hour:
            USER_CATCHES_HOURLY.clear()

        is_new_day = current_time.date() > self.last_spawn_time.date()

        old_time_of_day = 'day' if 7 <= self.last_spawn_time.hour < 19 else 'night'
        new_time_of_day = 'day' if 7 <= current_time.hour < 19 else 'night'
        is_day_night_transition = old_time_of_day != new_time_of_day

        if current_time.hour in (6, 7, 18, 19):
            self.time_of_day = DAWN if current_time.hour in (6, 7) else DUSK
        else:
            self.time_of_day = DAY if self.is_day else NIGHT

        if is_new_day or is_day_night_transition:
            USER_CATCHES_DAILY.clear()

            # todo: implement in V 3.0
            if is_day_night_transition:
                self.is_day = not self.is_day

            self.define_environment_and_spawn_pool(environment_id=self.current_environment.environment_id, variant_no=1 if self.is_day else 2)

        self.last_spawn_time = current_time