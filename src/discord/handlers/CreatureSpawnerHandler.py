import asyncio
import ssl
import threading
import time
import traceback
from copy import deepcopy
from datetime import datetime

from discord.ext.commands import Bot

from src.commons.CommonFunctions import flip_coin
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.buttonhandlers.CatchButton import TGOMMOCatchButtonView
from src.discord.embeds.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.objects.CreatureRarity import *
from src.discord.objects.TGOCreature import TGOCreature, TEST_SPAWN_POOL
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.general_constants import DISCORD_SA_CHANNEL_ID_TGOMMO


class CreatureSpawnerHandler:
    def __init__(self, discord_bot: Bot):
        self.discord_bot = discord_bot

        self.are_creatures_spawning = True

        self.current_environment = get_tgommo_db_handler().get_environment_by_dex_and_variant_no(dex_no=1, variant_no=1)
        self.creature_spawn_pool = TEST_SPAWN_POOL

        self.last_spawn_time = datetime.now()
        self.is_night = False  # todo - planned for v 2.0 night update


    # kicks off the creature spawner
    def start_creature_spawner(self):
        # todo - randomize the environment and variant to pull from multiple environments, planned for v 3.0 environment update
        self._define_environment_and_spawn_pool(environment_id=1, variant_no=1)
        asyncio.create_task(self._creature_spawner())


    # Toggles whether creatures are spawning or not
    def toggle_creature_spawner(self, ctx):
        self.are_creatures_spawning = not self.are_creatures_spawning
        return "creatures are now spawning" if self.are_creatures_spawning else "creatures are no longer spawning"


    # Loads a particular environment and defines the spawn pool for that environment
    def _define_environment_and_spawn_pool(self, environment_id: int, variant_no: int):
        current_environment_info = get_tgommo_db_handler().get_environment_by_dex_and_variant_no(dex_no=environment_id, variant_no=variant_no)
        self.current_environment = TGOEnvironment(environment_id=current_environment_info[0], name=current_environment_info[1], variant_name=current_environment_info[2], dex_no=current_environment_info[3], variant_no=current_environment_info[4], location=current_environment_info[5], description=current_environment_info[6], img_root=current_environment_info[7], is_night_environment=current_environment_info[8], in_circulation=current_environment_info[9], encounter_rate=current_environment_info[10])

        # Retrieve & Define Spawn Pool
        self.creature_spawn_pool = []
        creature_links = get_tgommo_db_handler().get_creatures_from_environment(environment_id=self.current_environment.environment_id)

        for creature_link in creature_links:
            local_name = creature_link[2]
            creature_info = get_tgommo_db_handler().get_creature_by_dex_and_variant_no(dex_no=creature_link[0], variant_no=creature_link[1])

            creature = TGOCreature(creature_id= creature_info[0], name=creature_info[1] if local_name == '' else local_name, variant_name=creature_info[2], dex_no=creature_info[3], variant_no=creature_info[4],full_name=creature_info[5], scientific_name=creature_info[6], kingdom=creature_info[7], description=creature_info[8], img_root=creature_info[9], encounter_rate=creature_info[10], rarity=get_rarity_by_name(creature_link[3]))
            self.creature_spawn_pool.append(creature)


    # Main loop that determines when to spawn creatures at random intervals
    async def _creature_spawner(self):
        while self.are_creatures_spawning:
            # check if a new day has begun or if a day/night transition has occurred
            self._handle_time_change()
            creature = await self.creature_picker()

            try:
                await self.spawn_creature(creature= creature)

                # 12% chance to spawn a duplicate of common and uncommon creatures
                spawn_duplicate = await flip_coin(total_iterations=3) and creature.rarity in (COMMON, UNCOMMON, RARE)
                while spawn_duplicate:
                    # 6% chance to spawn more duplicates
                    await self.spawn_creature(creature=deepcopy(creature))
                    spawn_duplicate = await flip_coin(total_iterations=4)
            except (ssl.SSLError, Exception) as e:
                # Handle all errors in a single block
                error_type = "SSL Error" if isinstance(e, ssl.SSLError) else "Error"
                print(f"{error_type} occurred during creature spawning- skipping to next creature - {e}")
                traceback.print_exc()
                await asyncio.sleep(5)

            # wait between 8 and 12 minutes before spawning another creature - will spawn 120 - 180 creatures a day
            await asyncio.sleep(random.uniform(8, 12) *60)


    # Spawns a creature and sends a message to the discord channel
    async def spawn_creature(self, creature: TGOCreature):
        creature_embed = CreatureEmbedHandler(creature=creature, environment=self.current_environment).generate_spawn_embed()

        # Send a message to the approval queue with a button to give XP
        spawn_message = await self.discord_bot.get_channel(DISCORD_SA_CHANNEL_ID_TGOMMO).send(
            view=TGOMMOCatchButtonView(discord_bot=self.discord_bot, message=f'Catch',creature=creature, environment=self.current_environment),
            files=[creature_embed[1], creature_embed[2]],
            embed=creature_embed[0]
        )

        # Create separate task for despawn
        thread = threading.Thread(target=self._handle_despawn, args=(creature, spawn_message))
        thread.daemon = True
        thread.start()


    # Picks a random creature from the spawn pool
    async def creature_picker(self):
        rarity = get_rarity()

        available_creatures = [creature for creature in self.creature_spawn_pool if creature.rarity == rarity]
        selected_index = random.randint(0, len(available_creatures)-1) if len(available_creatures) > 1 else 0

        selected_creature = deepcopy(available_creatures[selected_index])

        if random.randint(0,250) == 1:
            selected_creature.rarity = MYTHICAL
            selected_creature.img_root += '_S'

        return selected_creature


    # Handles despawning of a creature after its despawn time has elapsed
    def _handle_despawn(self, creature: TGOCreature, spawn_message):
        time.sleep(creature.despawn_time * 60)  # Convert minutes to seconds
        try:
            # Try to fetch the message to check if it still exists
            channel = self.discord_bot.get_channel(spawn_message.channel.id)
            asyncio.run_coroutine_threadsafe(channel.fetch_message(spawn_message.id), self.discord_bot.loop).result()
        except discord.NotFound:
            print('Message was already deleted, do nothing')
            return

        creature_embed = CreatureEmbedHandler(creature=creature, environment=self.current_environment).generate_spawn_embed(is_spawn_message=False)
        asyncio.run_coroutine_threadsafe(spawn_message.delete(), self.discord_bot.loop)
        asyncio.run_coroutine_threadsafe(
            self.discord_bot.get_channel(DISCORD_SA_CHANNEL_ID_TGOMMO).send(
                files=[creature_embed[1]],
                embed=creature_embed[0]
            ), self.discord_bot.loop
        )


    # Checks if a new day has begun or if a day/night transition has occurred, and if so, reloads the environment and spawn pool
    def _handle_time_change(self):
        current_time = datetime.now()

        is_new_day = current_time.date() > self.last_spawn_time.date()
        is_day_night_transition = False #todo

        if is_new_day:  # New Day
            self._define_environment_and_spawn_pool(environment_id=1, variant_no=1)
        elif is_day_night_transition:  # todo Day/Night Transition - planned for v 2.0 night update
            self.is_night = not self.is_night

        self.last_spawn_time = current_time

