from twitchAPI.chat import Chat, EventData, ChatMessage
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from src.obs.OBSWebsocket import OBSWebSocket


class TwitchBot:

    def __init__(self, client_id: str, app_secret: str, target_channel: str, refresh_token: str, access_token: str, obs_websocket: OBSWebSocket):
        self.app_id = client_id
        self.app_secret = app_secret

        self.twitch_bot = Twitch(self.app_id, self.app_secret)

        self.user_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
        self.target_channel = target_channel

        self.obs_websocket = obs_websocket

        self.twitch_chat = None
        self.refresh_token = None
        self.access_token =  None


    # ------------
    #    EVENTS
    # ------------
    # runs when a new chat message appears
    async def on_message(self, msg: ChatMessage):
        print(f'{msg.user.display_name} sent a message - {msg.text}')

    async def on_sub(self, msg: ChatMessage):
        print(f'{msg.user.display_name} has subscribed - {msg.text}')

    # runs when bot is initialized
    async def on_ready(self, ready_event: EventData):
        await ready_event.chat.join_room(self.target_channel)
        print(f'twitch bot has started! - Listening on {self.target_channel}')

    async def run_bot(self):
        auth = UserAuthenticator(self.twitch_bot, self.user_scope)

        if self.access_token is None or self.refresh_token is None:
            self.access_token, self.refresh_token = await auth.authenticate()

        await self.twitch_bot.set_user_authentication(self.access_token, self.user_scope, self.refresh_token)

        self.twitch_chat = await Chat(self.twitch_bot)

        # Register Events
        self.twitch_chat.register_event(ChatEvent.READY, self.on_ready)
        self.twitch_chat.register_event(ChatEvent.MESSAGE, self.on_message)
        self.twitch_chat.register_event(ChatEvent.SUB, self.on_sub)

        # Start the chatbot
        self.twitch_chat.start()


    # ------------
    # MISC METHODS
    # ------------
    async def twitch_send_message_to_chat(self, message: str):
        await self.twitch_chat.discord_send_message(self.target_channel, message)

    async def twitch_reply_to_chat_message(self, ctx: ChatMessage, message: str):
        await ctx.reply(message)


    # ------------------
    # GETTERS / SETTERS
    # ------------------
    def get_twitch_chat(self):
        return Chat(self.twitch_bot)