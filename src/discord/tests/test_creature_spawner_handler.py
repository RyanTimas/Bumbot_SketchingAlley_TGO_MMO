import asyncio
import unittest
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, Mock, patch
from dataclasses import FrozenInstanceError

from src.discord.game_features.creature_enounter import CreatureSpawnerHandler as spawner_module
from src.discord.objects.TGOCreature import TGOCreature


class CreatureSpawnerHandlerTests(unittest.IsolatedAsyncioTestCase):
    def make_handler(self):
        handler = object.__new__(spawner_module.CreatureSpawnerHandler)
        handler.discord_bot = SimpleNamespace()
        handler.current_environment = SimpleNamespace(name="Forest", timezone="timezone")
        handler.time_of_day = spawner_module.DAY
        handler.active_bonuses = []
        handler.pending_environment = None
        handler.spawn_event = asyncio.Event()
        handler.are_creatures_spawning = True
        handler._spawner_running = False
        handler._spawner_start_claimed = False
        handler._spawner_task = None
        handler._environment_scheduler_task = None
        handler._environment_change_task = None
        handler._despawn_tasks = set()
        handler._afk_notification_tasks = set()
        handler._logger = __import__("logging").getLogger("test_creature_spawner_handler")
        return handler

    @staticmethod
    def make_creature(name, rarity, kingdom="forest", time_to_despawn=30):
        creature = SimpleNamespace(
            name=name,
            kingdom=kingdom,
            local_rarity=SimpleNamespace(name=rarity),
            time_to_despawn=time_to_despawn,
        )
        creature.set_creature_rarity = Mock(
            side_effect=lambda new_rarity: setattr(creature, "local_rarity", new_rarity)
        )
        creature.refresh_spawn_and_despawn_time = Mock()
        return creature

    def test_bonus_context_preserves_overwrite_semantics_and_is_immutable(self):
        handler = self.make_handler()
        handler.active_bonuses = [
            SimpleNamespace(item_id="kingdom-one", item_type="normal"),
            SimpleNamespace(item_id="kingdom-two", item_type="normal"),
            SimpleNamespace(item_id="normal-charm", item_type="normal"),
        ]

        with patch.object(spawner_module, "KINGDOM_CHARM_MAP", {"kingdom-one": "forest", "kingdom-two": "desert"}), \
                patch.object(spawner_module, "CHARM_IDS", {"normal-charm"}), \
                patch.object(spawner_module.random, "randint", side_effect=[1, 1]):
            context = handler._resolve_spawn_bonus_context()

        self.assertEqual(context.kingdom, "desert")
        self.assertTrue(context.normal_charm_active)
        self.assertEqual(context.source_bonus_ids, ("kingdom-one", "kingdom-two", "normal-charm"))
        with self.assertRaises(FrozenInstanceError):
            context.kingdom = "desert"

    async def test_creature_picker_returns_none_for_empty_pool(self):
        handler = self.make_handler()
        handler.creature_spawn_pool = []

        self.assertIsNone(await handler.creature_picker(rarity="common"))

    async def test_creature_picker_returns_none_when_requested_rarity_is_unavailable(self):
        handler = self.make_handler()
        handler.creature_spawn_pool = [self.make_creature("Common", "Common")]

        self.assertIsNone(await handler.creature_picker(rarity="Rare"))

    async def test_creature_picker_preserves_kingdom_fallback_and_pool_isolation(self):
        handler = self.make_handler()
        rare_creature = self.make_creature("Rare", "Rare", kingdom="forest")
        handler.creature_spawn_pool = [rare_creature]

        selected = await handler.creature_picker(rarity="Common", kingdom={"forest"})

        self.assertEqual(selected.name, "Rare")
        self.assertIsNot(selected, rare_creature)
        self.assertEqual(rare_creature.local_rarity.name, "Rare")
        selected = await handler.creature_picker(rarity="Common", kingdom={"forest"})
        self.assertIsNot(selected, rare_creature)

    async def test_creature_picker_prepares_mythical_timing_without_discord_io(self):
        handler = self.make_handler()
        creature = self.make_creature("Mythical", "Common", time_to_despawn=90)

        candidate = handler._prepare_spawn_candidate(
            selected_creature=creature,
            rarity=spawner_module.TGOMMO_RARITY_MYTHICAL,
            refresh_timing=True,
        )

        self.assertIs(candidate.creature, creature)
        creature.refresh_spawn_and_despawn_time.assert_called_once_with(
            timezone="timezone",
            minute_offset=720,
        )

    async def test_spawn_creature_skips_none_candidate_without_presentation(self):
        handler = self.make_handler()
        handler.creature_picker = AsyncMock(return_value=None)
        channel = SimpleNamespace(send=AsyncMock())
        handler.discord_bot.get_channel = Mock(return_value=channel)

        with patch.object(spawner_module, "CreatureEmbedHandler") as embed_handler, \
                patch.object(spawner_module, "CreatureEncounterView") as encounter_view:
            result = await handler.spawn_creature(rarity="common")

        self.assertIsNone(result)
        channel.send.assert_not_awaited()
        embed_handler.assert_not_called()
        encounter_view.assert_not_called()

    async def test_spawn_creature_registers_despawn_only_after_successful_send(self):
        handler = self.make_handler()
        creature = self.make_creature("Common", "Common")
        channel = SimpleNamespace(send=AsyncMock(return_value=SimpleNamespace(id=1)))
        handler.discord_bot.get_channel = Mock(return_value=channel)
        handler._duplicate_creature_spawner = AsyncMock()

        class EmbedHandler:
            def __init__(self, *args, **kwargs):
                pass

            def generate_spawn_embed(self):
                return "embed", "thumb", "encounter"

        class EncounterView:
            def __init__(self, *args, **kwargs):
                pass

        original_create_task = asyncio.create_task
        with patch.object(spawner_module, "CreatureEmbedHandler", EmbedHandler), \
                patch.object(spawner_module, "CreatureEncounterView", EncounterView), \
                patch.object(spawner_module.asyncio, "create_task", side_effect=original_create_task):
            await handler.spawn_creature(creature=cast(TGOCreature, creature), user=SimpleNamespace(user_id=1))

        channel.send.assert_awaited_once()
        self.assertEqual(len(handler._despawn_tasks), 1)
        handler._duplicate_creature_spawner.assert_not_awaited()
        for task in tuple(handler._despawn_tasks):
            task.cancel()
        await asyncio.gather(*handler._despawn_tasks, return_exceptions=True)

    def test_transcendant_creature_bypasses_mythical_conversion(self):
        handler = self.make_handler()
        creature = self.make_creature("Transcendant", spawner_module.TRANSCENDANT.name)

        with patch.object(spawner_module, "random") as random_module:
            result = handler.perform_mythical_check(creature)

        self.assertIs(result, creature)
        random_module.randint.assert_not_called()

    async def test_start_claim_prevents_duplicate_scheduler_tasks(self):
        handler = self.make_handler()
        started = asyncio.Event()

        async def spawn_loop():
            started.set()
            await asyncio.Event().wait()

        async def environment_loop():
            await asyncio.Event().wait()

        handler._creature_spawner = spawn_loop
        handler._environment_change_check_scheduler = environment_loop

        handler.start_creature_spawner()
        first_spawn_task = handler._spawner_task
        first_environment_task = handler._environment_scheduler_task
        handler.start_creature_spawner()

        self.assertIs(handler._spawner_task, first_spawn_task)
        self.assertIs(handler._environment_scheduler_task, first_environment_task)
        self.assertTrue(handler._spawner_start_claimed)

        await started.wait()
        await handler._cleanup_tasks()

        self.assertFalse(handler._spawner_start_claimed)
        self.assertFalse(handler._spawner_running)
        self.assertFalse(handler._despawn_tasks)

    async def test_despawn_awaits_fetch_delete_and_notification_in_order(self):
        handler = self.make_handler()
        order = []
        creature = cast(TGOCreature, SimpleNamespace(time_to_despawn=17))
        spawn_message = SimpleNamespace(
            id=42,
            channel=SimpleNamespace(id=7),
        )

        async def fetch_message(message_id):
            order.append(("fetch", message_id))

        async def delete_message():
            order.append("delete")

        spawn_message.delete = delete_message
        channel = SimpleNamespace(fetch_message=fetch_message)
        notification_channel = SimpleNamespace()

        async def send_notification(**kwargs):
            order.append("notification")

        notification_channel.send = send_notification
        handler.discord_bot.get_channel = lambda channel_id: (
            channel if channel_id == 7 else notification_channel
        )
        def handle_afk_trap_catch(creature):
            order.append("afk")
            return False

        handler.handle_afk_trap_catch = handle_afk_trap_catch

        class EmbedHandler:
            def __init__(self, *args, **kwargs):
                pass

            def generate_despawn_embed(self):
                order.append("embed")
                return "embed", "image"

        with patch.object(spawner_module, "CreatureEmbedHandler", EmbedHandler), \
                patch.object(spawner_module.asyncio, "sleep", new=AsyncMock()) as sleep:
            await handler._despawn_creature(creature, spawn_message)

        sleep.assert_awaited_once_with(17)
        self.assertEqual(
            order,
            [("fetch", 42), "delete", "afk", "embed", "notification"],
        )

    async def test_cleanup_cancels_despawn_and_scheduler_tasks(self):
        handler = self.make_handler()

        async def never_finishes():
            await asyncio.Event().wait()

        handler._spawner_task = asyncio.create_task(never_finishes())
        handler._environment_scheduler_task = asyncio.create_task(never_finishes())
        handler._environment_change_task = asyncio.create_task(never_finishes())
        handler._despawn_tasks.add(asyncio.create_task(never_finishes()))
        handler._spawner_running = True
        handler._spawner_start_claimed = True

        await handler._cleanup_tasks()

        self.assertFalse(handler._spawner_running)
        self.assertFalse(handler._spawner_start_claimed)
        self.assertIsNone(handler._spawner_task)
        self.assertIsNone(handler._environment_scheduler_task)
        self.assertIsNone(handler._environment_change_task)
        self.assertFalse(handler._despawn_tasks)

    async def test_scheduler_task_failure_is_consumed_and_logged(self):
        handler = self.make_handler()

        async def fails():
            raise RuntimeError("scheduler failure")

        task = asyncio.create_task(fails())
        handler._spawner_task = task
        await asyncio.sleep(0)

        with self.assertLogs("test_creature_spawner_handler", level="ERROR") as logs:
            handler._scheduler_task_completed(task)

        self.assertIn("Spawner task failed", logs.output[0])
        self.assertIsNone(handler._spawner_task)

    async def test_cancelled_afk_notification_is_not_logged_as_failure(self):
        handler = self.make_handler()

        async def never_finishes():
            await asyncio.Event().wait()

        task = asyncio.create_task(never_finishes())
        handler._afk_notification_tasks.add(task)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

        with self.assertNoLogs("test_creature_spawner_handler", level="ERROR"):
            handler._afk_notification_task_completed(task)

        self.assertNotIn(task, handler._afk_notification_tasks)

    async def test_cleanup_cancels_tracked_afk_notification_tasks(self):
        handler = self.make_handler()

        async def never_finishes():
            await asyncio.Event().wait()

        task = asyncio.create_task(never_finishes())
        handler._afk_notification_tasks.add(task)

        await handler._cleanup_tasks()

        self.assertTrue(task.cancelled())
        self.assertFalse(handler._afk_notification_tasks)


if __name__ == "__main__":
    unittest.main()
