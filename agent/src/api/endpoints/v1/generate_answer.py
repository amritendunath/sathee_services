from fastapi import APIRouter, Depends, HTTPException, status, Request
from models.generate_answer import GenerationResponse, GenerationRequest, ErrorResponse, GraphResponse, StartRequest
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import HumanMessage
from fastapi import FastAPI, HTTPException, Header
from agents.builder import build_graph_quick, build_graph_think
import logging
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os, uuid
from datetime import datetime
from utils.database import Database
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import asyncio
from fastapi import FastAPI
import contextvars
from langchain_openai import ChatOpenAI
from agents.memory import get_memory
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from sse_starlette.sse import EventSourceResponse
import json
from uuid import uuid4
from typing import Optional
from langchain_core.messages import AIMessage
from utils.config import Settings
setting = Settings()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # openai_api_key=setting.OPEN_API_KEY,
    # openai_api_base=setting.OPEN_API_BASE,
    # model_name=setting.OPEN_API_MODEL_NAME_QUICK
quick_mode_llm = ChatOpenAI(
    openai_api_key=os.environ.get("OPEN_API_KEY"),
    openai_api_base=os.environ.get("OPEN_API_BASE"),
    model_name=os.environ.get("OPEN_API_MODEL_NAME_QUICK")
)
    # openai_api_key=setting.OPEN_API_KEY,
    # openai_api_base=setting.OPEN_API_BASE,
    # model_name=setting.OPEN_API_MODEL_NAME_THINK
think_mode_llm = ChatOpenAI(
    openai_api_key=os.environ.get("OPEN_API_KEY"),
    openai_api_base=os.environ.get("OPEN_API_BASE"),
    model_name=os.environ.get("OPEN_API_MODEL_NAME_THINK")
)

app = FastAPI()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not set in environment")

ALGORITHM = "HS256"
logging.info("Loaded graph")

async def get_database() -> Database:
    return Database.get_instance()

@app.on_event("startup")
async def startup():
    # database = Database.get_instance()
    # await database.create_indexes()
    # await initialize_database()
    # asyncio.create_task(generation_streaming())
    # asyncio.create_task(get_chat_history())
    # asyncio.create_task(get_chat_sessions())
    # asyncio.create_task(create_new_session())
    # asyncio.create_task(end_session())
    pass


prompt = ChatPromptTemplate.from_template(
    """You are an AI Assistant. Generate a small name based on the following query of max 30 letters or 4 words and min of 1 letters or 1 words based on query: {query}
    - Don't use any special character
    """
)
chain = prompt | quick_mode_llm | StrOutputParser()

# Generate a session title for a particular session based on user query using LLM: AI Generated
async def create_session_title(query: str) -> str:
    """Generate a session title using the LLM."""
    return await chain.ainvoke({"query": query})

# Extract the user_id from the token
async def extract_user_id_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        ehr_id: str = payload.get("user_ehr_id")
        if ehr_id is None:
            raise credentials_exception
        return ehr_id
    except JWTError:
        raise credentials_exception

# Extract the user_email from the token
async def extract_user_email_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception

# saving the chat session into the db: database
async def persist_chat_message(
        user_id: str, 
        session_id: str, 
        query: str, 
        messages: str, 
        database: Database = Depends(get_database)
    ):   
    first_query = not await database.chats.find_one(
        {"user_id": user_id, "session_id": session_id}
    )

    if first_query:
        # session_title = await create_session_title(query)
        session_title = query[:35]
    else:
        result = await database.chats.find_one(
            {"user_id": user_id, "session_id": session_id}
        )
        session_title = result["session_title"]  # Access session_title *after* awaiting

    chat_document = {
        "user_id": user_id,
        "session_id": session_id,
        "message": query,
        "response": messages,
        "timestamp": datetime.utcnow(),
        "session_title": session_title,
    }
    await database.chats.insert_one(chat_document)




###################################################################################################
###################################################################################################

# All Endpoint of agent_service


# New Chat Session
@router.post('/generate-stream/new-session')
async def create_new_session(
    user_id: str = Depends(extract_user_id_from_token), 
    database: Database = Depends(get_database)
    ):
    try:
        # Create new session
        active_session = await database.sessions.find_one({
            "user_id": user_id,
            "end_time": None
        })

        if active_session: await database.sessions.update_one(
                {"_id": active_session["_id"]},
                {
                    "$set": {
                        "end_time":
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                },
            )
        session_id = str(uuid.uuid4())
        await database.sessions.insert_one({
            "user_id": user_id,
            "session_id": session_id,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
        })

        logger.info(f"New session created with ID: {session_id}")
        return session_id
    except Exception as e:
        logger.error(f"Failed to create new session: {str(e)}")
        raise


# Close The Current Chat Session
@router.post("/generate-stream/end-session")
async def end_session(
    user_id: str = Depends(extract_user_id_from_token), 
    database: Database = Depends(get_database)
    ):
    try:


        # Find the active session for the user
        active_session = await database.sessions.find_one({
            "user_id": user_id,
            "end_time": None
        })

        if active_session:
            # Update the session end time
            await database.sessions.update_one(
                {"_id": active_session["_id"]},
                {
                    "$set": {
                        "end_time":
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                },
            )
        return JSONResponse({
            "message": "Session ended successfully",
            "session_id": active_session["session_id"],
        })

    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# All Chat Session Of An User
@router.get("/generate-stream/chat-sessions")
async def get_chat_sessions(
    user_id: str = Depends(extract_user_id_from_token), 
    database: Database = Depends(get_database)
    ):
    try:
        pipeline = [
            {
                "$match": {
                    "user_id": user_id
                }
            },
            {
                "$group": {
                    "_id": "$session_id",
                    "title": {
                        "$first": "$session_title"
                    },
                    "timestamp": {
                        "$first": "$timestamp"
                    },
                }
            },
            {
                "$sort": {
                    "timestamp": -1
                }
            },
        ]

        # sessions = list(db.chats.aggregate(pipeline))
        sessions = await database.chats.aggregate(pipeline).to_list(length=None)

        # Format the sessions to ensure proper date handling
        formatted_sessions = []
        for session in sessions:
            formatted_session = {
                "session_id": session["_id"],
                "session_title": session["title"],
                "timestamp": (session["timestamp"].isoformat() if isinstance(
                    session["timestamp"], datetime) else session["timestamp"]),
            }
            formatted_sessions.append(formatted_session)

        return JSONResponse(content={"sessions": formatted_sessions})
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# All Chat History Of A Particular Chat Session Of An User
@router.get("/generate-stream/chat-history/{session_id}")
async def get_chat_history(
    session_id: str, user_id: str = Depends(extract_user_id_from_token), 
    database: Database = Depends(get_database)
    ):
    try:
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "session_id": session_id
                }
            },
            {
                "$sort": {
                    "timestamp": 1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "message": 1,
                    "response": 1,
                    "timestamp": 1,
                    "type": 1,
                    "tag": 1,
                }
            },
        ]

        # chat_history = list(db.chats.aggregate(pipeline))
        chat_history = await database.chats.aggregate(pipeline).to_list(length=None)

        formatted_history = []
        for chat in chat_history:
            # Convert datetime to ISO format string for JSON serialization
            timestamp = (chat["timestamp"].isoformat() if isinstance(
                chat["timestamp"], datetime) else chat["timestamp"])

            formatted_history.append({
                "message": chat["message"],
                "type": "user",
                "timestamp": timestamp
            })
            formatted_history.append({
                "message": chat["response"],
                "type": "bot",
                "timestamp": timestamp
            })

        return JSONResponse(content={"chat_history": formatted_history})
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


#########################################################################################################
#########################################################################################################
# Chat Streaming Endpoint
@router.post("/generate-stream/", response_model=GenerationResponse, responses={500: {"model": ErrorResponse}})
async def generation_streaming(
        request: GenerationRequest,
        thread_id: str = Header("111222", alias="X-THREAD-ID"),
        token: str = Depends(oauth2_scheme),
        memory: AsyncSqliteSaver = Depends(get_memory),
        database: Database = Depends(get_database)
):

    query = request.query
    queryModeType = request.queryModeType
    logging.info(
        f"Received the Query - {query} & thread_id - {thread_id} and Type: {queryModeType}"
    )
    try:
        # Decode the token to get user information
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        ehr_id: str = payload.get("user_ehr_id")
        existing_session = await database.sessions.find_one({
            "user_id": ehr_id,
            "end_time": None
        })
        if not existing_session:
            session_id = str(uuid.uuid4())
            await database.sessions.insert_one({
                "user_id":
                ehr_id,
                "session_id":
                session_id,
                "start_time":
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "end_time":
                None
            })
            logger.info(f"Created new session {session_id} for user {ehr_id}")
        else:
            session_id = existing_session["session_id"]
            logger.info(
                f"Using existing session {session_id} for user {ehr_id}")

        inputs = [HumanMessage(content=query)]
        state = {
            "messages": inputs,
            "mode": queryModeType,
            "email": user_email,
            "user_id": ehr_id,
        }
        config = RunnableConfig(configurable={
            "thread_id": thread_id,
            "recursion_limit": 10
        })
        if queryModeType == 'quick':
            graph = build_graph_quick(quick_mode_llm, memory)
            response = await graph.ainvoke(input=state, config=config)
            logging.info("Generated Answer from Graph")
            dialog_states = response["dialog_state"]
            dialog_state = dialog_states[-1] if dialog_states else "primary_assistant"
            messages = response["messages"][-1].content
        elif queryModeType == 'think':
            graph = build_graph_think(think_mode_llm, memory)
            response = await graph.ainvoke(input=state, config=config)
            print("resonse,", response)
            logging.info("Generated Answer from Graph")
            dialog_states = response["dialog_state"]
            dialog_state = dialog_states[
                -1] if dialog_states else "primary_assistant"
            messages = response["messages"][-1].content

        await persist_chat_message(ehr_id, session_id, query, messages, database)
        return JSONResponse({
            "dialog_state": dialog_state if dialog_state else "",
            "answer": messages if messages else "",
            "session_id": session_id
        })

    except Exception as e:
        logger.error(f"Error in chat processing: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Failed to process chat: {str(e)}")
########################################################################################################
########################################################################################################
run_configs = {}

@router.post("/generate-stream/create", response_model=GraphResponse)
async def create_streaming(
    request: StartRequest, 
    token: Optional[str] = Depends(oauth2_scheme),
    database: Database = Depends(get_database)
    ):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        # thread_id = str(uuid4())
        ehr_id = await extract_user_id_from_token(token)
        email = await extract_user_email_from_token(token)
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # logger.info(f"JWT Payload: {payload}")
        # email: str = payload.get("sub")
        # ehr_id: str = payload.get("user_ehr_id")
        # logger.info("email", email)
        # logger.info("ehr_id", ehr_id)
        existing_session = await database.sessions.find_one({
            "user_id": ehr_id,
            "end_time": None
        })
        if not existing_session:
            session_id = str(uuid.uuid4())
            await database.sessions.insert_one({
                "user_id": ehr_id,
                "session_id": session_id,
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": None
            })
            logger.info(f"Created new session {session_id} for user {ehr_id}")
        else:
            session_id = existing_session["session_id"]
            logger.info(f"Using existing session {session_id} for user {ehr_id}")

        thread_id = session_id    

        run_configs[thread_id] = {
            "type": "start",
            "query": request.query,
            "user_id": ehr_id,
            "email": email,
            "queryModeType": request.queryModeType,
            "session_id": session_id
        }

        return GraphResponse(
            thread_id=thread_id,
            answer = None
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



@router.get("/generate-stream/{thread_id}", responses={500: {"model": ErrorResponse}})
async def generation_streaming(
    request: Request,
    thread_id: str,
    database: Database = Depends(get_database),
    memory: AsyncSqliteSaver = Depends(get_memory)
):
    try:
        if thread_id not in run_configs:
            return {"error": "Thread ID not found. You must first call the create"}
        
        run_data = run_configs[thread_id]
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        queryModeType = run_data["queryModeType"]
        query = run_data["query"]
        user_id = run_data["user_id"]
        email = run_data["email"]
        inputs = [HumanMessage(content=query)]
        # logger.info("queryModeType",queryModeType)
        # input_state = None
        if run_data["type"] == "start":
            event_type = "start"
            user_id = run_data["user_id"]
            input_state = {
                "messages":  inputs,
                "user_id": user_id, 
                "email": email
            }
        else:
            return None
        
        existing_session = await database.sessions.find_one({
            "user_id": user_id,
            "end_time": None
        })
        if not existing_session:
            session_id = str(uuid.uuid4())
            await database.sessions.insert_one({
                "user_id": user_id,
                "session_id": session_id,
                "start_time":
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "end_time":
                None
            })
            logger.info(f"Created new session {session_id} for user {user_id}")
        else:
            session_id = existing_session["session_id"]
            logger.info(
                f"Using existing session {session_id} for user {user_id}")

        async def event_stream():
            # session_id = run_data.get("session_id")
            # if not session_id:
            #     session_id = thread_id
            initial_data = json.dumps({'thread_id': thread_id})
            yield {"event": event_type, "data": initial_data}
            if queryModeType == "quick":
                graph = build_graph_quick(quick_mode_llm, memory)
            elif queryModeType == 'think':
                graph = build_graph_think(think_mode_llm, memory)
            full_msg_content = ""
            try:
                async for msg, metadata in graph.astream(input_state, config, stream_mode="messages"):
                    if await request.is_disconnected():
                        print("DEBUG: Client disconnected, breaking stream loop")
                        break
                    
                    if metadata.get('langgraph_node') in ['primary_assistant', 'medical_info', 'get_info', 'appointment_info', 'hospital_info']:
                        token_data = json.dumps({"content": msg.content})
                        print(f"DEBUG: Sending token event with data: {token_data[:30]}...")
                        yield {"event": "token", "data": token_data}
                        full_msg_content += msg.content

                await persist_chat_message(user_id, session_id, query, full_msg_content, database)
                
                if thread_id in run_configs:
                    del run_configs[thread_id]

            except Exception as e:
                logging.error(f"Error in streaming: {str(e)}")
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)})
                }
            finally:
                yield {"event": "close"}

        return EventSourceResponse(event_stream())

    except Exception as e:
        logger.error(f"Error in chat processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")
    






# Chat Streaming Endpoint
# @router.get("/generate-stream/{thread_id}", responses={500: {"model": ErrorResponse}})
# async def generation_streaming(
#     request: Request,
#     thread_id: str,
#     # token: str = Depends(oauth2_scheme),
#     # memory: AsyncSqliteSaver = Depends(get_memory),
#     database: Database = Depends(get_database),
# ):
#     try:
#         if thread_id not in run_configs:
#             return {"error": "Thread ID not found. You must first call the create"}
#         run_data = run_configs[thread_id]
#         config={
#             "configurable": {
#                 "thread_id": thread_id
#             }
#         }
#         input_state = None
#         if run_data["type"] == "start":
#             event_type = "start"
#             user_id = await run_data["user_id"]
#             input_state = {
#                 "messages": [HumanMessage(content=run_data["human_request"])],
#   # Add mode since we're using quick_mode_llm
#             }
#             # input_state = {"human_request": run_data["human_request"]}
#         else:
#             return None
        

#         # inputs = [HumanMessage(content=query)]
#         # state = {
#         #     "messages": inputs,
#         #     # "mode": queryModeType,
#         #     # "email": user_email,
#         #     # "user_id": ehr_id,
#         # }
#         # config = RunnableConfig(configurable={
#         #     "thread_id": thread_id,
#         #     "recursion_limit": 10
#         # })
#         async def event_stream():
#             initial_data = json.dumps({'thread_id': thread_id})
#             yield{"event": event_type, "data": initial_data}
#             graph = build_graph_quick(quick_mode_llm)
#             try:
#                 for msg, metadata in graph.stream(input_state, config):
#                     if await request.is_disconnected():
#                         break
#                     if metadata.get('langgraph_node') in ['primary_assistant']:
#                         token_data = json.dumps({"content": msg.content})
#                         print(f"DEBUG: Sending token event with data: {token_data[:30]}...")
#                         yield {"event": "token", "data": token_data}
#                 if thread_id in run_configs:
#                     print(f"DEBUG: Cleaning up thread_id={thread_id} from run_configs")
#                     del run_configs[thread_id]
#                 # yield {
#                 #     "event": "message",
#                 #     "data": json.dumps({
#                 #         # "dialog_state": dialog_state if dialog_state else "",
#                 #         "answer": msg.content,
#                 #         # "session_id": session_id,
#                 #         "content": msg.content
#                 #     })
#                 # }
#             except Exception as e:
#                 logging.error(f"Error in streaming: {str(e)}")
#                 yield {
#                     "event": "error",
#                     "data": json.dumps({"error": str(e)})
#                 }
#             finally:
#                 yield {"event": "close"}  # Signal the end of the stream
#         # try:
#         #         await your_api_endpoint_function(ehr_id, session_id, query, messages, database) # Put it here
#         # except Exception as e:
#         #         logging.error(f"Error in saving data: {str(e)}")
#         return EventSourceResponse(event_stream())

#     except Exception as e:
#         logger.error(f"Error in chat processing: {str(e)}")
#         raise HTTPException(status_code=500,
#                             detail=f"Failed to process chat: {str(e)}")





        # async def event_stream():
        #     initial_data = json.dumps({'thread_id': thread_id})
        #     yield {"event": event_type, "data": initial_data}
        #     graph = build_graph_quick(quick_mode_llm)
        #     try:
        #         async for item in graph.astream(input_state, config):
        #             print(f"DEBUG: astream yielded: {item}")
        #             if await request.is_disconnected():
        #                 break

        #             if isinstance(item, dict):
        #                 for key, value in item.items():
        #                     # Extract message content
        #                     if isinstance(value.get("messages"), AIMessage): #Value should be AIMessage object
        #                         msg_content = value["messages"].content

        #                         # Extract tool_calls if present
        #                         tool_calls = value["messages"].additional_kwargs.get("tool_calls")
        #                         if tool_calls:
        #                             print("tool_calls exist, skipping")
        #                             continue

        #                         # Check langgraph_node in metadata
        #                         metadata = value.get('__annotations__', {})  # Or however metadata is accessed
        #                         langgraph_node = metadata.get('langgraph_node')

        #                         if langgraph_node in ['primary_assistant', 'medical_info', 'get_info', 'appointment_info', 'hospital_info']:
        #                             token_data = json.dumps({"content": msg_content})
        #                             print(f"DEBUG: Sending token event with data: {token_data[:30]}...")
        #                             yield {"event": "token", "data": token_data}

        #             else:
        #                 logging.warning(f"Unexpected item type from graph.astream: {type(item)}")
        #                 yield {"event": "error", "data": json.dumps({"error": "Unexpected item type from graph.astream"})}

        #     except Exception as e:
        #         logging.error(f"Error in streaming: {str(e)}")
        #         yield {
        #             "event": "error",
        #             "data": json.dumps({"error": str(e)})
        #         }
        #     finally:
        #         yield {"event": "close"}


                        # Use regular for loop since graph.stream returns a regular generator
                # async for item in graph.astream(input_state, config):
                    # print(f"DEBUG: astream yielded: {item}")
                    # if await request.is_disconnected():
                    #     break

                    # if isinstance(item, dict):
                    #     for key, value in item.items():
                    #         # Extract message content
                    #         if isinstance(value.get("messages"), list): #Value should be list of AIMessage object
                    #             msg_content = value["messages"][0].content

                    #             # Extract tool_calls if present
                    #             if 'tool_calls' in value["messages"][0].additional_kwargs:
                    #                 print("tool_calls exist, skipping")
                    #                 continue

                    #             # Check langgraph_node in metadata
                    #             metadata = value.get('__annotations__', {})  # Or however metadata is accessed
                    #             langgraph_node = metadata.get('langgraph_node')

                    #             if langgraph_node in ['primary_assistant', 'medical_info', 'get_info', 'appointment_info', 'hospital_info']:
                    #                 token_data = json.dumps({"content": msg_content})
                    #                 print(f"DEBUG: Sending token event with data: {token_data[:30]}...")
                    #                 yield {"event": "token", "data": token_data}
                    #         else:
                    #             msg_content = value["messages"].content
                    #             token_data = json.dumps({"content": msg_content})
                    #             yield {"event": "token", "data": token_data}
                    
                    # else:
                    #     logging.warning(f"Unexpected item type from graph.astream: {type(item)}")
                    #     yield {"event": "error", "data": json.dumps({"error": "Unexpected item type from graph.astream"})}
                