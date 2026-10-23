import asyncio
import unittest
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, patch

from src.discord.game_features.creature_enounter import CreatureSpawnerHandler as spawner_module
from src.discord.objects.TGOCreature import TGOCreature


class CreatureSpawnerHandlerTests(unittest.IsolatedAsyncioTestCase):
    def make_handler(self):
        handler = object.__new__(spawner_module.CreatureSpawnerHandler)
        handler.discord_bot = SimpleNamespace()
        handler.current_environment = SimpleNamespace(name="Forest")
        handler.pending_environment = None
        handler.spawn_event = asyncio.Event()
        handler.are_creatures_spawning = True
        handler._spawner_running = False
        handler._spawner_start_claimed = False
        handler._spawner_task = None
        handler._environment_scheduler_task = None
        handler._environment_change_task = None
        handler._despawn_tasks = set()
        return handler

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


if __name__ == "__main__":
    unittest.main()
