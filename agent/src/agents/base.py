from agents.AgentState import State
from langchain_core.runnables import Runnable, RunnableConfig


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state, config=config)

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
# from langchain_core.messages import AIMessage
# from agents.AgentState import State
# from langchain_core.runnables import Runnable, RunnableConfig

# class Assistant:
#     def __init__(self, runnable: Runnable):
#         self.runnable = runnable

#     def __call__(self, state: State, config: RunnableConfig):
#         while True:
#             result = self.runnable.invoke(state, config=config)

#             # Extract content safely
#             content = getattr(result, "content", None)
#             tool_calls = result.additional_kwargs.get("tool_calls", []) if hasattr(result, "additional_kwargs") else []

#             # Handle blank or unhelpful response
#             if not tool_calls and (
#                 not content or
#                 (isinstance(content, list) and not any(c.get("text") for c in content))
#             ):
#                 messages = state["messages"] + [("user", "Respond with a real output.")]
#                 state = {**state, "messages": messages}
#             else:
#                 break

#         return {"messages": [result]}  # Ensure always list of messages

# class Assistant:
#     def __init__(self, runnable: Runnable):
#         self.runnable = runnable

#     def __call__(self, state: State, config: RunnableConfig):
#         while True:
#             result = self.runnable.invoke(state, config=config)

#             if not hasattr(result, 'tool_calls') and (
#                 not result
#                 or isinstance(result, list)
#                 and not result[0].get("text")
#             ):
#                 messages = state["messages"] + [("user", "Respond with a real output.")]
#                 state = {**state, "messages": messages}
#             else:
#                 break
#         return {"messages": result}
# from langchain_core.messages import AIMessage, BaseMessage
# from agents.AgentState import State
# from langchain_core.runnables import Runnable, RunnableConfig
# class Assistant:
#     def __init__(self, runnable: Runnable):
#         self.runnable = runnable

#     def __call__(self, state: State, config: RunnableConfig):
#         while True:
#             result = self.runnable.invoke(state, config=config)

#             # Case 1: List of messages (multi-step chains or routers)
#             if isinstance(result, list):
#                 if not result or not getattr(result[0], "content", "").strip():
#                     messages = state["messages"] + [("user", "Respond with a real output.")]
#                     state = {**state, "messages": messages}
#                     continue
#                 break

#             # Case 2: Single message (like AIMessage)
#             if isinstance(result, AIMessage):
#                 if not result.content.strip():
#                     messages = state["messages"] + [("user", "Respond with a real output.")]
#                     state = {**state, "messages": messages}
#                     continue
#                 break

#             # Fallback: result type unexpected
#             if not result or not getattr(result, "content", "").strip():
#                 messages = state["messages"] + [("user", "Respond with a real output.")]
#                 state = {**state, "messages": messages}
#                 continue

#             break  # Valid message

#         # Always return a list of messages
#         return {"messages": result if isinstance(result, list) else [result]}

# from langchain_core.messages import BaseMessage
# from langchain_core.runnables import Runnable, RunnableConfig
# from agents.AgentState import State

# class Assistant:
#     def __init__(self, runnable: Runnable):
#         self.runnable = runnable

#     def __call__(self, state: State, config: RunnableConfig):
#         def valid(msg):
#             return isinstance(msg, BaseMessage) and getattr(msg, "content", "").strip()

#         result = self.runnable.invoke(state, config=config)

#         # Retry once if needed
#         if isinstance(result, list):
#             if result and valid(result[0]):
#                 return {"messages": result}
#         elif valid(result):
#             return {"messages": [result]}

#         # Add retry signal
#         state["messages"].append(("user", "Please respond with a real output."))
#         result = self.runnable.invoke(state, config=config)

#         # Return the raw result properly wrapped
#         if isinstance(result, list):
#             return {"messages": result}
#         elif isinstance(result, BaseMessage):
#             return {"messages": [result]}
#         else:
#             return {"messages": []}

