from pymongo import MongoClient, DESCENDING
import asyncio
import os
import json
import datetime

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

    async def add_gode(self, user):
        """
        Get all mod info from a user
        """
        loop = asyncio.get_event_loop()
        actual = await loop.run_in_executor(None, self.db.gode.find_one, {'user': user})
        print("research find", actual)
        now = datetime.datetime.now()
        if actual is None:
            print("On doit avoir zero result")
            res = await loop.run_in_executor(None, self.db.gode.insert_one, {'user': user, 'date': now, 'gode': 1})
        else:
            if actual['date'].day != now.day:
                print("gode totu ok")
                res = await loop.run_in_executor(None, self.db.gode.update_one, {'user': user}, {'$set': {'date': now}, '$inc': {'gode': 1}})
            else:
                print("meme jour")
                return False
        return True

    async def get_gode(self, user):
        loop = asyncio.get_event_loop()
        actual = await loop.run_in_executor(None, self.db.gode.find_one, {'user': user})
        return actual

    async def get_gode_top(self, limit):
        loop = asyncio.get_event_loop()
        r = await loop.run_in_executor(None, self.db.gode.find, {})
        return r.sort("gode", DESCENDING).limit(limit)


