import asyncio
import time
import unittest
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, patch

from src.commons.AsyncBlocking import run_serialized_blocking
from src.discord.game_features.creature_enounter import CatchFunctions
from src.discord.game_features.creature_enounter import CreatureEncounterView as encounter_module
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment


class CatchCallbackResponsivenessTests(unittest.IsolatedAsyncioTestCase):
    async def test_serialized_blocking_work_does_not_block_event_loop(self):
        ticker_ran = asyncio.Event()

        def blocking_work():
            time.sleep(0.05)
            return "complete"

        blocking_task = asyncio.create_task(run_serialized_blocking(blocking_work))
        await asyncio.sleep(0)
        ticker_ran.set()

        self.assertTrue(ticker_ran.is_set())
        self.assertEqual(await blocking_task, "complete")

    async def test_async_catch_adapter_preserves_sync_result(self):
        expected = {"catch_id": 123, "user_profile": object()}
        creature = cast(TGOCreature, SimpleNamespace())
        environment = cast(TGOEnvironment, SimpleNamespace())

        with patch.object(CatchFunctions, "_catch_creature_sync", return_value=expected) as sync_catch:
            result = await CatchFunctions.catch_creature_async(7, creature, environment)

        self.assertIs(result, expected)
        sync_catch.assert_called_once_with(7, creature, environment, None, False)

    async def test_post_catch_rewards_are_scheduled_after_critical_callback(self):
        view = object.__new__(encounter_module.CreatureEncounterView)
        view.discord_bot = None
        view.creature = SimpleNamespace(creature_id=11, name="Test Creature", catch_time=0)
        view.environment = SimpleNamespace()
        view.spawn_user = None
        view.caught = False
        view.interaction_lock = asyncio.Lock()
        view.successful_catch_embed_handler = None
        view.successful_catch_message = None
        view._post_catch_tasks = set()
        view._logger = __import__("logging").getLogger(__name__)
        view._is_user_catch_limit_reached = lambda user_id: False

        post_rewards_started = asyncio.Event()

        async def post_rewards(interaction, catch_id):
            post_rewards_started.set()

        view._process_post_catch_rewards = post_rewards

        class Response:
            async def defer(self, **kwargs):
                return None

        class Followup:
            def __init__(self):
                self.messages = []

            async def send(self, content, **kwargs):
                self.messages.append(content)

        followup = Followup()
        interaction = SimpleNamespace(
            user=SimpleNamespace(id=7),
            response=Response(),
            followup=followup,
            channel=SimpleNamespace(send=AsyncMock(return_value=SimpleNamespace())),
            message=SimpleNamespace(delete=AsyncMock()),
        )

        fake_caught_view = object()
        fake_embed_handler = object()
        catch_result = {
            "catch_id": 99,
            "catch_embed": object(),
            "catch_image": object(),
        }

        with patch.object(encounter_module, "check_if_user_can_interact_with_view", new=AsyncMock(return_value=True)), \
                patch.object(encounter_module, "catch_creature_async", new=AsyncMock(return_value=catch_result)), \
                patch.object(encounter_module, "CreatureEmbedHandler", return_value=fake_embed_handler), \
                patch.object(encounter_module, "CreatureCaughtView", return_value=fake_caught_view):
            callback = view.catch_button_callback()
            await callback(interaction)

        self.assertIn("Success!! you've successfully caught the Test Creature", followup.messages)
        self.assertFalse(post_rewards_started.is_set())
        await asyncio.gather(*view._post_catch_tasks)
        self.assertTrue(post_rewards_started.is_set())


if __name__ == "__main__":
    unittest.main()
