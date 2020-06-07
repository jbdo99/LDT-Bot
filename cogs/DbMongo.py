from pymongo import MongoClient
import asyncio
import os
import json

with open(os.path.dirname(__file__)[:-4] + 'server.json') as f:
    permissions_config = json.load(f)

class DbMongo:
    def __init__(self, host, username, password):
        """
        MongoDB Interface
        :param host: mongodb host
        :param username: mongodb user's username
        :param password: mongodb user's password
        """
        print("conection to", host)
        client = MongoClient("mongodb://{username}:{password}@{host}".format(
            username=username,
            password=password,
            host=host
        ))
        self.db = client.ldt

    async def get_all_mod_from(self, user):
        """
        Get all mod info from a user
        """
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, self.db.mod.find, {'user': user})
        return list(res)

    async def delete_mod(self, user, objid):
        """
        delete mod info from a user
        """
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, self.db.mod.delete_one, {'user': user, '_id': objid})

    async def add_log_mod(self, moderation_type, user, duration, date, reason, provider):
        """
        Get all mod info from a user
        """
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, self.db.mod.insert_one, {'type': moderation_type,
                                                                        'user': user,
                                                                        'duration': duration,
                                                                        'date': date,
                                                                        'reason': reason,
                                                                        'author': provider})
        return res
