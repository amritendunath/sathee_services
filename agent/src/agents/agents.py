# from langchain_core.prompts.chat import ChatPromptTemplate
# from langchain_core.runnables import RunnableLambda, RunnableMap, RunnableBranch

# def get_runnable(llm, tools, agent_prompt):
#     prompt_template = ChatPromptTemplate.from_messages(
#         [
#             ("system", agent_prompt),
#             ("placeholder", "{messages}"),
#         ]
#     )

#     agent_runnable = prompt_template | llm.bind_tools(tools)
#     return agent_runnable

# from langchain_core.runnables import RunnableLambda, RunnableMap, RunnableBranch
# def get_runnable(llm, tools, agent_prompt):
#     # user_id = "123456789"
#     # email = "abc@example.com"
#     prompt_template = ChatPromptTemplate.from_messages(
#         [
#             ("system", agent_prompt + "\nUser ID: {user_id}\nEmail: {email}"),
#             ("placeholder", "{messages}"),
#         ]
#     )
#     # Combine the messages and user info using RunnableLambda
#     # combine_runnable = RunnableMap(
#     #     {
#     #         "messages": lambda x: x["messages"],
#     #         "user_id": lambda x: x.get("user_id", "unknown"),
#     #         "email": lambda x: x.get("email", "unknown@example.com"),
#     #     }
#     # )
#     combine_runnable = RunnableMap({
#     "messages": lambda x: x["messages"],
#     "user_id": lambda x: print("🔍 USER_ID in runnable:", x.get("user_id")) or x.get("user_id"),
#     "email": lambda x: print("🔍 EMAIL in runnable:", x.get("email")) or x.get("email"),
#     })

#     agent_runnable = combine_runnable | prompt_template | llm
#     return agent_runnable
    # agent_runnable = combine_runnable | print_config | prompt_template | llm
    # def print_config(x, config):
    #     print("Config:", config)  # Add this line
    #     return x
    # agent_runnable = combine_runnable | prompt_template | llm.bind_tools(tools)


from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap
from typing import Dict, Any

def get_runnable(llm, tools, agent_prompt):
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", agent_prompt + "\nUser ID: {user_id}\nEmail: {email}\nMode:{mode}"),
            ("placeholder", "{messages}"),
        ]
    )

    def extract_prompt_input(state: Dict[str, Any])-> Dict[str, Any]:
        print("🧪 Incoming state:", state)
        return {
            "messages": state["messages"],
            "user_id": state.get("user_id"),
            "email": state.get("email"),
            "mode": state.get("mode")
        }
    
    return (
        RunnableLambda(extract_prompt_input)
        | prompt_template
        | llm.bind_tools(tools)
    )
    # combine_runnable
    # combine_runnable = RunnableMap({
    #     "messages": lambda x: x["messages"],
    #     "user_id": lambda x: print("🔍 USER_ID in runnable:", x.get("user_id")) or x.get("user_id"),
    #     "email": lambda x: print("🔍 EMAIL in runnable:", x.get("email")) or x.get("email"),
    # })
