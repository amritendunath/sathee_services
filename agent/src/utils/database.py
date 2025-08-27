# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo.server_api import ServerApi
# from dotenv import load_dotenv
# import os
# import logging
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# load_dotenv()


# class Database:
#     def __init__(self):
#         # self.client = MongoClient(os.getenv('MONGODB_URI'), server_api=ServerApi('1')) 
#         self.client = AsyncIOMotorClient(os.getenv('MONGODB_URI'), server_api=ServerApi('1'))
#         self.db = self.client["sathi_chatbot"]

#         # Collections
#         self.users = self.db["users"]
#         self.chats = self.db["chats"]
#         self.appointments = self.db["appointments"]
#         self.medical_records = self.db["medical_records"]
#         self.sessions = self.db["sessions"]

#     async def create_indexes(self):
#         # Create indexes
#         await self.users.create_index("email", unique=True)
#         await self.chats.create_index([("user_email", 1), ("timestamp", -1)])
#         await self.chats.create_index("session_id")
#         await self.appointments.create_index([("user_email", 1), ("appointment_date", 1)])
#         await self.medical_records.create_index("user_email", unique=True)
#         await self.sessions.create_index([("user_email", 1), ("end_time", 1)])
#         await self.sessions.create_index("session_id", unique=True)

# db: Database = None

# async def initialize_database():
#     global db
#     logger.info("Initializing database...")
#     db = Database()
#     await db.create_indexes()
#     logger.info("Database initialized")
#     return db  # Return the database instance




# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo.server_api import ServerApi
# from dotenv import load_dotenv
# import os
# import logging

# load_dotenv()

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# class Database:
#     _instance = None  # Singleton instance

#     def __init__(self):
#         if Database._instance is not None:
#             raise Exception("Cannot create another instance of Database. Use get_instance() instead.")

#         logger.info("Connecting to MongoDB...")
#         self.client = AsyncIOMotorClient(os.getenv('MONGODB_URI'), server_api=ServerApi('1'))
#         self.db = self.client["sathi_chatbot"]
#         logger.info("Connected to MongoDB")

#         # Collections
#         self.users = self.db["users"]
#         self.chats = self.db["chats"]
#         self.appointments = self.db["appointments"]
#         self.medical_records = self.db["medical_records"]
#         self.sessions = self.db["sessions"]
#         Database._instance = self

#     @classmethod
#     def get_instance(cls):
#         if cls._instance is None:
#             cls._instance = Database()
#         return cls._instance

#     async def create_indexes(self):
#         logger.info("Creating indexes...")
#         # Create indexes
#         await self.users.create_index("email", unique=True)
#         await self.chats.create_index([("user_email", 1), ("timestamp", -1)])
#         await self.chats.create_index("session_id")
#         await self.appointments.create_index([("user_email", 1), ("appointment_date", 1)])
#         await self.medical_records.create_index("user_email", unique=True)
#         await self.sessions.create_index([("user_email", 1), ("end_time", 1)])
#         await self.sessions.create_index("session_id", unique=True)
#         logger.info("Indexes created")



from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Database:
    _instance = None  # Singleton instance

    def __init__(self):
        if Database._instance is not None:
            raise Exception("Cannot create another instance of Database. Use get_instance() instead.")

        logger.info("Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(os.getenv('MONGODB_URI'), server_api=ServerApi('1'))
        self.db = self.client["sathi_chatbot"]
        logger.info("Connected to MongoDB")

        # Collections
        self.users = self.db["users"]
        self.chats = self.db["chats"]
        self.appointments = self.db["appointments"]
        self.medical_records = self.db["medical_records"]
        self.sessions = self.db["sessions"]
        Database._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    async def create_indexes(self):
        logger.info("Creating indexes...")
        # Create indexes
        await self.users.create_index("email", unique=True)
        await self.chats.create_index([("user_email", 1), ("timestamp", -1)])
        await self.chats.create_index("session_id")
        await self.appointments.create_index([("user_email", 1), ("appointment_date", 1)])
        await self.medical_records.create_index("user_email", unique=True)
        await self.sessions.create_index([("user_email", 1), ("end_time", 1)])
        await self.sessions.create_index("session_id", unique=True)
        logger.info("Indexes created")