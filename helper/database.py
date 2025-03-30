import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:

    def __init__(self, uri, database_name):
        if not uri:
            print("⚠️ No database URL provided. Running without a database.")
            self._client = None
            self.madflixbotz = None
            self.col = None
            return

        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.madflixbotz = self._client[database_name or "default_db"]  # Use default if empty
        self.col = self.madflixbotz.user

    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None,
            format_template=None
        )

    async def add_user(self, b, m):
        if not self.col:
            return  # Skip if DB is disabled
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)
            await send_log(b, u)

    async def is_user_exist(self, id):
        if not self.col:
            return False
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        if not self.col:
            return 0
        return await self.col.count_documents({})

    async def get_all_users(self):
        if not self.col:
            return []
        return self.col.find({})

    async def delete_user(self, user_id):
        if not self.col:
            return
        await self.col.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, id, file_id):
        if not self.col:
            return
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        if not self.col:
            return None
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        if not self.col:
            return
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        if not self.col:
            return None
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)

    async def set_format_template(self, id, format_template):
        if not self.col:
            return
        await self.col.update_one({'_id': int(id)}, {'$set': {'format_template': format_template}})

    async def get_format_template(self, id):
        if not self.col:
            return None
        user = await self.col.find_one({'_id': int(id)})
        return user.get('format_template', None)

    async def set_media_preference(self, id, media_type):
        if not self.col:
            return
        await self.col.update_one({'_id': int(id)}, {'$set': {'media_type': media_type}})

    async def get_media_preference(self, id):
        if not self.col:
            return None
        user = await self.col.find_one({'_id': int(id)})
        return user.get('media_type', None)


# Initialize database (Handles missing DB gracefully)
madflixbotz = Database(Config.DB_URL, Config.DB_NAME)
