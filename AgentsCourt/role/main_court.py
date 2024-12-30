from colorama import Fore
from role_playing import RolePlaying
from utils import print_text_animated
from Self_Feedback.task_init import TaskInit
from Self_Feedback.feedback import Feedback
from Self_Feedback.task_iterate import TaskIterate
import json
import copy
from tqdm import tqdm
import time 

def court_interact(Task, chat_turn_limit):
    case_dict = Task
    case_name = case_dict["案件名"]
    CASE_TEMPLATE = """基本案情: {case_details}\n案件类型: {case_type}"""
    task_prompt = CASE_TEMPLATE.format(case_details=case_dict["基本案情"], case_type=case_dict["类别"]+"案件")
    case_plaintiff = case_dict["原告（公诉）"]
    case_defendant = case_dict["被告"]
    case_defendant_detail = case_dict["被告基本情况"]

    plaintiff_prompt = case_dict['原告诉请判令（公诉机关指控）']
    if case_dict['被告代理人辩护'] == '无' and case_dict['被告陈述'] == '无':
        defendant_prompt = '无'
    elif case_dict['被告代理人辩护'] != '无' and case_dict['被告陈述'] != '无':
        defendant_prompt = case_dict['被告代理人辩护']
    elif case_dict['被告代理人辩护'] != '无' and case_dict['被告陈述'] == '无':
        defendant_prompt = case_dict['被告代理人辩护']
    elif case_dict['被告代理人辩护'] == '无' and case_dict['被告陈述'] != '无':
        defendant_prompt = case_dict['被告陈述']
        
    role_play_session = RolePlaying(
        ('plaintiff', plaintiff_prompt),
        ('defendant', defendant_prompt),
        case_plaintiff=case_plaintiff,
        case_defendant=case_defendant,
        case_defendant_detail=case_defendant_detail,
        task_prompt=task_prompt,
        #with_task_specify=True,
    )

    #print(Fore.YELLOW + f"\n当前案号: {case_name}\n{task_prompt}\n\nInteractive simulating...\n")
    
    n = 0
    assistant_msg, _ = role_play_session.init_chat()

    court_record = []
    while n < chat_turn_limit:
        n += 1
        assistant_return, user_return= role_play_session.step(assistant_msg)
            #######
        assistant_msg, assistant_terminated, assistant_info = assistant_return
        user_msg, user_terminated, user_info = user_return
        #print("user_msg:", user_msg)
        #print_text_animated(Fore.BLUE + f"Plaintiff:\n\n{user_msg.content}\n")
        #print_text_animated(Fore.GREEN + f"Defendant:\n\n{assistant_msg.content}\n")
        user_content = user_msg.content
        assistant_content = assistant_msg.content
        if user_content.startswith('[原告控诉]') or user_content.startswith('[原告发言]'):
            court_record.append(user_content)
        
        if assistant_content.startswith('[被告辩解]'):
            court_record.append(assistant_content)

    return court_record




if __name__ == "__main__":
    
    with open("/SimuCourt1.3.json","r") as file:
        data_all = json.load(file)

    fail_id = []
    court_record_dict = {}

    for case_dict in tqdm(data_all):
        try:
            case_num = case_dict["案号"]
            court_record = {}
            iter_num = 1
            while len(court_record) < 7 and iter_num < 5:
                print('Number of iter: {}'.format(iter_num))
                court_record = court_interact(Task=case_dict, chat_turn_limit=4)
                court_record_dict[case_num] = court_record
                iter_num += 1
            
            print('Number of Court records: {}'.format(len(court_record)))
            #print('{} Saved!'.format(case_num))
        except Exception as e:
            case_num = case_dict["案号"]
            fail_id.append(case_num)
    
    with open("/court_records.json", "w", encoding='utf-8') as file:
        json.dump(court_record_dict, file, ensure_ascii=False, indent=4)

    


