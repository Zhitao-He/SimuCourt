from typing import Dict, List, Optional, Tuple
from generators import SystemMessageGenerator
from messages import AssistantChatMessage, ChatMessage, UserChatMessage
from typeC import ModelType, RoleType
from chat_agent import ChatAgent
import os
import openai
import time
import re


def llm(prompt):
    result = openai.ChatCompletion.create(
    model= 'gpt-3.5-turbo',
    messages=[
            {"role": "user", "content": prompt},
        ], 
    )
    output = result["choices"][0]["message"]["content"]
    return output


class RolePlaying:
    
    def __init__(
        self,
        user_role,
        assistant_role,
        case_plaintiff,
        case_defendant,
        case_defendant_detail,
        task_prompt= ""
    ) -> None:
        
        self.task_prompt = task_prompt 
        user_role_name = user_role[0]
        assistant_role_name = assistant_role[0]
        plaintiff_prompt = user_role[1]
        defendant_prompt = assistant_role[1]

        sys_msg_generator = SystemMessageGenerator()
        
        sys_msg_meta_dicts = [{
            "<ASSISTANT_ROLE>": assistant_role_name,
            "<USER_ROLE>": user_role_name,
            "<PLAINTIFF>": plaintiff_prompt,
            "<DEFENDANT>": defendant_prompt,
            "<PLAINTIFF_NAME>": case_plaintiff,
            "<DEFENDANT_NAME>": case_defendant,
            "<DEFENDANT_DETAIL>": case_defendant_detail,
            "<TASK>": task_prompt,
        }] * 2
        
        self.assistant_sys_msg, self.user_sys_msg = (
            sys_msg_generator.from_dicts(
                meta_dicts=sys_msg_meta_dicts,
                role_tuples=[
                    (assistant_role_name, RoleType.ASSISTANT),
                    (user_role_name, RoleType.USER),
                ],
            ))

        self.assistant_agent = ChatAgent(
            self.assistant_sys_msg
        )
        self.user_agent = ChatAgent(
            self.user_sys_msg
        )

    def init_chat(self):
        
        self.assistant_agent.reset()
        self.user_agent.reset()

        assistant_msg = AssistantChatMessage(
            role_name=self.assistant_sys_msg.role_name,
            content=self.task_prompt)

        user_msg = UserChatMessage(role_name=self.user_sys_msg.role_name,
                                   content=self.task_prompt)
        
        msgs, _, _ = self.assistant_agent.step(user_msg) 

        return assistant_msg, msgs

    def process_messages(
        self,
        messages: List[ChatMessage],
    ) -> ChatMessage:
        if len(messages) == 0:
            raise ValueError("No messages to process.")
        if len(messages) > 1 :
            raise ValueError("Got than one message to process. "
                             f"Num of messages: {len(messages)}.")
        else:
            processed_msg = messages[0]

        return processed_msg

    def step(
        self,
        assistant_msg: ChatMessage
    ):

        user_msgs, user_terminated, user_info = self.user_agent.step(
            assistant_msg.to_user_chat_message())


        if user_terminated:
            return ((None, None, None), (None, user_terminated, user_info))
        
        user_msg = self.process_messages(user_msgs)
        
        
        self.user_agent.update_messages(user_msg)

        
        (assistant_msgs, assistant_terminated,
         assistant_info) = self.assistant_agent.step(
             user_msg.to_user_chat_message())
        if assistant_terminated:
            return ((None, assistant_terminated, assistant_info),
                    (user_msg, user_terminated, user_info))
        assistant_msg = self.process_messages(assistant_msgs)
        self.assistant_agent.update_messages(assistant_msg)
        

        return (
            (assistant_msg, assistant_terminated, assistant_info),
            (user_msg, user_terminated, user_info)
        )
