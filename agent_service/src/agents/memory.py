import aiosqlite
from typing import AsyncGenerator
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


db_path = "checkpoints.db"
conn = None  # Global connection variable

async def get_memory() -> AsyncGenerator[AsyncSqliteSaver, None]:
    """
    Async Dependency that yields the AsyncSqliteSaver
    """
    global conn  # Use the global connection
    if conn is None:
        conn = await aiosqlite.connect(db_path)  # Only connect if not already connected
    memory = AsyncSqliteSaver(conn)
    try:
        yield memory
    finally:
        pass  # Do not close the connection here