from typing import Dict, Generator, List, Optional, Set, Tuple
from messages import SystemMessage, SystemMessageType
import os
from typeC import ModelType, RoleType




def get_system_prompt(role):
    if role == 'plaintiff':
        template_path = os.path.join('/system_prompt/plaintiff_message.txt')
        with open(template_path, "r") as f:
            template = f.read()
    else:
        template_path = os.path.join('/system_prompt/defendant_message.txt')
        with open(template_path, "r") as f:
            template = f.read()
    
    return template


class SystemMessageGenerator:
    """System message generator for agents.
    """

    def __init__(self):
        
        user_prompt_template = get_system_prompt(role='plaintiff')
        assistant_prompt_template = get_system_prompt(role='defendant')

        self.sys_prompts = dict()
        self.sys_prompts[RoleType.USER] = user_prompt_template
        self.sys_prompts[RoleType.ASSISTANT] = assistant_prompt_template
        
    def from_dict(
        self,
        meta_dict,
        role_tuple,
    ):
        # assistant_role_name, RoleType.ASSISTANT
        role_name, role_type = role_tuple
        # assistant_prompt_template
        sys_prompt = self.sys_prompts[role_type]
        # 
        sys_prompt = self.replace_keywords(meta_dict, sys_prompt)
        return SystemMessage(role_name=role_name, role_type=role_type,
                             meta_dict=meta_dict, content=sys_prompt)

    def from_dicts(
        self,
        meta_dicts,
        role_tuples,
    ):
        if len(meta_dicts) != len(role_tuples):
            raise ValueError(
                "The number of meta_dicts and role_types should be the same.")

        return [
            self.from_dict(meta_dict, role_tuple)
            for meta_dict, role_tuple in zip(meta_dicts, role_tuples)
        ]

    @staticmethod
    def replace_keywords(
        meta_dict,
        sys_prompt,
    ):
        for key, value in meta_dict.items():
            sys_prompt = sys_prompt.replace(key, value)
        return sys_prompt


