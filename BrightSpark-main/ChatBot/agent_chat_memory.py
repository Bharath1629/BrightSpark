import os
from langchain.memory import ConversationBufferWindowMemory
from datetime import datetime
from langchain_community.chat_message_histories import SQLChatMessageHistory
message_history = SQLChatMessageHistory(session_id= datetime.now().strftime("%d%m%Y %H:%M"), connection_string='mysql+mysqldb://root:h\^Bs+^AdG$#nEV=@34.31.88.232/team1')


def get_memory():
    return ConversationBufferWindowMemory(k=3, memory_key='chat_history', return_messages=True, chat_memory=message_history)