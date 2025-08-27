from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from api.api_router import generate_answer_router
import asyncio
import uvicorn
from utils.database import Database 
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")  # Ensure basic logging is configured

local = os.environ.get("LOCAL_URL")
prod = os.environ.get("PROD_URL")
# async def run_in_background():
#     await asyncio.sleep(5)
#     logger.info("I am running in background")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Lifespan event started.")  # Add log at the very beginning

#     try:
#         # Startup event
#         logger.info("Running startup event...")
#         database = Database.get_instance()
#         await database.create_indexes()
#         logger.info("Startup event completed.")
#         asyncio.create_task(run_in_background())
#         yield
#         # Shutdown event
#         logger.info("Running shutdown event...")
#         # Perform any cleanup tasks here (e.g., closing database connections)
#         logger.info("Shutdown event completed.")
#     except Exception as e:
#         logger.error(f"Exception during lifespan: {e}")  # Log any exceptions

#     logger.info("Lifespan event ended.")  # Add log at the very end


app = FastAPI(
    title="Doctor's Appointment Agentic Flow",
    version="6.0.0",
    description="Allow users to find and book availbility",
    openapi_url="/openapi.json",
    docs_url="/",
    # lifespan=lifespan
)
async def initialize_database():
    database = Database.get_instance()
    await database.create_indexes()

@app.on_event("startup")
async def startup():
    await initialize_database()


@app.get("/health")
async def health_check():
    return PlainTextResponse("OK")


origins = [
  local,
  prod
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(generate_answer_router)


print("Backend API is running")


asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
    # key = os.environ.get("SSL_KEY")
    # cert = os.environ.get("SSL_CERT")
    # if key and cert:
    #     uvicorn.run("main:app", host="0.0.0.0", port=8001, ssl_keyfile=key, ssl_certfile=cert)
    # else:
    #     print("SSL_KEY and SSL_CERT must be set in the environment")

