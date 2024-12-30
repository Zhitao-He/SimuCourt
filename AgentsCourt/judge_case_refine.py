# -*- coding: utf-8 -*-
import json
from openai import OpenAI
from tqdm import tqdm 
#from transformers import AutoTokenizer
import re
import time
import httpx

# 先采用prompt生成[法官分析]、[审判依据]和最终[判决]

# 1、先解析出上一步的[法官分析]、[审判依据]和最终[判决]
# 2、把[审判依据]中的法律法规 与 相似案例的法律法规作对比，取并集
# 3、把庭审记录取出来
# 4、提示词：相似案例，法律法规

def GPT_4(system_massage, prompt):
    time.sleep(10)
    client = OpenAI(
        base_url="https://oneapi.xty.app/v1", 
        api_key="sk-xxxxx",
        http_client=httpx.Client(
            base_url="https://oneapi.xty.app/v1",
            follow_redirects=True,
        ),
    )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        #model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": system_massage},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content.strip()

    
def split_clause(clause):
    law_name_match = re.search(r"《(.+?)》", clause)
    clause_number_match = re.search(r"第[\u4e00-\u9fa5\d]+条", clause)

    if law_name_match and clause_number_match:
        law_name = law_name_match.group(1)  
        clause_number = clause_number_match.group(0)
    else:
        law_name = None
        clause_number = None

    return law_name, clause_number


laws_base_path = 'all_laws.json'
with open(laws_base_path, 'r', encoding='utf-8') as file:
    laws_base = json.load(file)

def laws_useful(self_analysis_laws_list, candidate_laws_dict):
    useful_laws_list = self_analysis_laws_list
    for law1, law_dict in candidate_laws_dict.items():
        law_name1, clause_number1 = split_clause(law1)
        for law2 in self_analysis_laws_list:
            law_name2, clause_number2 = split_clause(law2)
            if law_name1 != law_name2 and clause_number1 != clause_number2:
                if law1 not in useful_laws_list:
                    useful_laws_list.append(law1)
    
    useful_laws_dict = {}
    for law in useful_laws_list:
        law_name, clause_number = split_clause(law)
        law_detial = laws_base[law_name][clause_number]
        useful_laws_dict[law] = law_detial
    
    return useful_laws_dict

# 法律条文细节
def macth_laws(laws_list):
    useful_laws_dict = {}
    for law in laws_list:
        try:
            law_name, clause_number = split_clause(law)
            law_detial = laws_base[law_name][clause_number]
            useful_laws_dict[law] = law_detial
        except:
            useful_laws_dict[law] = {}
        
    return useful_laws_dict

# 数据集
case_dataset = 'SimuCourt1.18(2).json'
with open(case_dataset, 'r', encoding='utf-8') as file:
    case_data = json.load(file)


# 案例
candidate_cases_path = 'case.json'
with open(candidate_cases_path, 'r', encoding='utf-8') as file:
    candidate_cases_dict = json.load(file)

# analysis_record 结果
analysis_record_path = 'analysis_record.json'
with open(analysis_record_path, 'r', encoding='utf-8') as file:
    analysis_record_dict = json.load(file)

# prompt
judge_final_path = '/system_prompt/judge_case_refine2.txt'
with open(judge_final_path, "r") as f:
    judge_final_system = f.read()

judge_analysis_revise_result = {}
error_list = []
error_case_list = []
# 庭审记录 + 基本案情
i = 0
for case_test in tqdm(case_data):
    if case_test["案号"] in error_case_list:
        
        candidate_cases = candidate_cases_dict[case_test['案号']][0]
        candidate1 = candidate_cases_dict[case_test['案号']][0]
        candidate1_laws = candidate1["审判依据"]
        if len(candidate_cases_dict[case_test['案号']]) > 1:
            candidate2 = candidate_cases_dict[case_test['案号']][1]
            candidate2_laws = candidate2["审判依据"]
            for k2, v2 in candidate2_laws.items():
                if k2 not in candidate1_laws:
                    candidate1_laws[k2] = v2

        # analysis_record 得到的法律法规
        analysis_record = analysis_record_dict[case_test['案号']]
        analysis_record_laws = analysis_record["审判依据"]
        analysis_record_laws_detial = macth_laws(analysis_record_laws)
        analysis_record_judge = analysis_record["法院意见"]
        analysis_record_result = analysis_record["判决结果"]
        analysis_record_result_str = ''
        for k,v in analysis_record_result.items():
            str_single = k + ':' + v + ';'
            analysis_record_result_str += str_single

        CASE_TEMPLATE1 = """
        你将收到一个以往判例及当前案件基本信息，这个以往案件与当前案件非常相近，请以这个以往案件为标准判例，根据其中的审判依据（法律法规）及审判结果对当前案件进行分析和裁决。
        以往判例信息：
        判例案件基本案情分析：{previous_case_analysis}
        判例案件类型：{previous_case_type}
        判例审判依据：{previous_case_laws}
        判例审判结果：{previous_case_result}
        
        请借鉴以上判例（案情分析、审判依据及审判结果）对以下的当前案件的审判意见、依据和结果进行进一步的改进（可能存在依据错误、结果错误等），并做出更加公正、严谨的最终裁决。
        当前案件信息：
        原告：{case_plaintiff}
        被告：{case_defendant}，被告基本情况：{case_defendant_detail}
        基本案情: {case_details}
        原告诉请判令：{case_plaintiff_detail}
        案件类型: {case_type}
        法院初步审判意见：{case_initial_judge}
        法院初步审判依据：{case_initial_laws}
        法院初步审判结果：{case_initial_result}
        最终裁决："""

        CASE_TEMPLATE2 = """
        你将收到一个以往判例及当前案件基本信息，这个以往案件与当前案件非常相近，请以这个以往案件为标准判例，根据其中的审判依据（法律法规）及审判结果对当前案件进行分析和裁决。
        以往判例信息：
        判例案件基本案情分析：{previous_case_analysis}
        判例案件类型：{previous_case_type}
        判例审判结果：{previous_case_result}
        可参考判例审判依据：{previous_case_laws}
        
        请借鉴以上判例（案情分析、审判依据及审判结果）对以下的当前案件的做出更加公正、严谨的最终裁决。
        当前案件信息：
        上诉人：{case_plaintiff}，上诉人基本情况：{case_defendant_detail}
        被上述人：{case_defendant}
        案件类型: {case_type}
        一审法院认定事实：{first_fact}
        一审法院意见：{first_analysis}
        一审法院审判依据：{first_laws}
        一审法院审判结果：{first_result}
        二审上诉请求：{second_appeal}
        二审查明事实：{second_fact}
        二审初步结果：{second_initial_result}
        可参考审判依据：{second_initial_laws}
        最终裁决："""

        
        if len(candidate_cases["content"]) > 1500:
            previous_case_analysis = candidate_cases["content"][:1500]
        else:
            previous_case_analysis = candidate_cases["content"]
        
        if len(str(candidate1_laws)) >  2200:
            candidate1_laws = str(candidate1_laws)[:2200]
        else:
            candidate1_laws = candidate1_laws

        
        # 基本案情
        task_prompt2 = CASE_TEMPLATE2.format(
            previous_case_type=candidate_cases["案件类型"],
            previous_case_analysis=previous_case_analysis,
            previous_case_laws=candidate1_laws,
            previous_case_result=candidate_cases["审判结果"],
            case_plaintiff=case_test["上诉人"], 
            case_defendant=case_test["被上诉人"],
            case_defendant_detail=case_test["上诉人基本情况"],
            case_type=case_test["类别"] + '案件',
            first_fact=case_test["一审法院认定事实"],
            first_analysis=case_test["一审法院意见"],
            first_laws=case_test["一审法院审判依据"],
            first_result=case_test["一审法院审判结果"],
            second_appeal=case_test["上诉请求"],
            second_fact=case_test["本院二审查明事实"],
            second_initial_result=analysis_record_result_str,
            second_initial_laws=analysis_record_laws_detial
            )
        
        # 基本案情
        
        try:
            judge_slef_analysis = GPT_4(judge_final_system, task_prompt2)
            judge_analysis_revise_result[case_test['案号']] = judge_slef_analysis
        except:
            print('Error:', case_test['案号'])
            error_list.append(case_test['案号'])


        with open('case_refine.json', 'w', encoding='utf-8') as file:
            json.dump(judge_analysis_revise_result, file, ensure_ascii=False, indent=4)
        i += 1
print(error_list)



    
