# import time
import datetime
import pymongo

from .singleton import Singleton


class Mongo(metaclass=Singleton):
    """Manage SQL connection, as well as basic user information
    """

    log = logging.getLogger()

    def __init__(self, url="mongodb://root:example@mongodb"):
        self.mongo_client = pymongo.MongoClient(url)


    async def on_ready(self):
        for guild in self.discord_client.guilds:
            self.log.info(f"Boot registration for {guild}")
            self.log.info(f"Register {len(guild.members)} members.")
            self.log.info(f"Register {len(guild.channels)} channels.")

        self.log.info("Mongo registered to receive commands!")


    async def on_message(self, message):
        self.log.debug(f"Got message: {message.content}")
        self.log.debug(f"       From: {message.author.name} ({message.author.id})")
        if message.guild:
            self.log.debug(f"         On: {message.guild} ({message.guild.id})")
        else:
            # Do not save or parse private channels
            return

        self.mongo_client.stats.channels.update_one(
            {'channel_id': message.channel.id},
            {
                '$inc': {
                    'messages': 1,
                    'characters': len(message.content),
                    'words': len(message.content.split()),
                    'embeds': len(message.embeds),
                    'mentions': len(message.mentions),
                    'channel_mentions': len(message.channel_mentions),
                    'role_mentions': len(message.role_mentions),
                    'attachments': len(message.attachments),
                },
                '$set': {
                    'name': message.channel.name,
                    'last_change': datetime.datetime.now(datetime.timezone.utc),
                },
                '$setOnInsert': {
                    'first_seen': datetime.datetime.now(datetime.timezone.utc),
                }
            },
            upsert=True,
        )

        self.mongo_client.stats.users.update_one(
            {'user_id': message.author.id},
            {
                '$inc': {
                    'messages': 1,
                    'characters': len(message.content),
                    'words': len(message.content.split()),
                    f'channels.{message.guild.id}.{message.channel.id}': 1,
                    'embeds': len(message.embeds),
                    'mentions': len(message.mentions),
                    'channel_mentions': len(message.channel_mentions),
                    'role_mentions': len(message.role_mentions),
                    'attachments': len(message.attachments),
                },
                '$set': {
                    'name': message.author.name,
                    'nick': message.author.nick if hasattr(message.author, 'nick') else None,
                    'last_change': datetime.datetime.now(datetime.timezone.utc),
                },
                '$setOnInsert': {
                    'first_seen': datetime.datetime.now(datetime.timezone.utc),
                }
            },
            upsert=True,
        )


    async def table_setup(self):
        """Setup any Mongo tables needed for this class
        """
        self.log.debug("Nothing to do for Mongo!")
