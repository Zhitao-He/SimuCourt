import json
import openai
from tqdm import tqdm 
import tiktoken

# 最终裁决

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def GPT_4(system_massage, prompt):
    
    response = openai.ChatCompletion.create(
        #model="gpt-3.5-turbo-1106",
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": system_massage}, 
                    {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content'].strip()
    
# 数据集
case_dataset = '1.4/SimuCourt1.3.json'
with open(case_dataset, 'r', encoding='utf-8') as file:
    case_data = json.load(file)

# 庭审记录
court_judge_path = '1.4/SimuCourt_GPT_3.5/judge_with_record.json'
with open(court_judge_path, 'r', encoding='utf-8') as file:
    court_judge = json.load(file)

# 案例
candidate_cases_path = 'retrieve_candi_case/case_number_candi_laws_detail1.json'
with open(candidate_cases_path, 'r', encoding='utf-8') as file:
    candidate_cases_dict = json.load(file)

# prompt
judge_final_path = '/system_prompt/judge_final.txt'
with open(judge_final_path, "r") as f:
    judge_final_system = f.read()

judge_final_result = {}
error_list = []
error_case_list = []
# 庭审记录 + 基本案情
for case_test in tqdm(case_data):
        # 相似案例
        candidate_cases = candidate_cases_dict[case_test['案号']][0]
        candidate1 = candidate_cases_dict[case_test['案号']][0]
        candidate1_laws = candidate1["审判依据"]
        if len(candidate_cases_dict[case_test['案号']]) > 1:
            candidate2 = candidate_cases_dict[case_test['案号']][1]
            
            candidate2_laws = candidate2["审判依据"]

            for k2, v2 in candidate2_laws.items():
                if k2 not in candidate1_laws:
                    candidate1_laws[k2] = v2

        # 庭审分析
        court_judge_analysis = court_judge[case_test['案号']]

        CASE_TEMPLATE = """
        你将收到一个以往判例及当前案件基本信息，这个以往案件与当前案件非常相近，请以这个以往案件为标准判例，根据其中的审判依据（法律法规）及审判结果对当前案件进行分析和裁决。
        以往判例信息：
        判例案件基本案情分析：{previous_case_analysis}
        判例案件类型：{previous_case_type}
        判例审判结果：{previous_case_result}
        
        请借鉴以上判例（审判依据及结果）对以下的当前案件进行公正的裁决：
        当前案件信息：
        原告：{case_plaintiff}
        被告：{case_defendant}，{case_defendant_detail}
        基本案情: {case_details}
        原告诉请判令：{case_plaintiff_detail}
        案件类型: {case_type}
        庭审过程分析：{case_court_record}
        请仔细参考以下法律条文：{previous_case_laws}
        最终裁决："""

        # 基本案情
        task_prompt = CASE_TEMPLATE.format(
            previous_case_type=candidate_cases["案件类型"],
            previous_case_analysis=candidate_cases["content"],
            previous_case_laws=candidate1_laws,
            previous_case_result=candidate_cases["审判结果"],
            case_plaintiff=case_test["原告（公诉）"], 
            case_defendant=case_test["被告"],
            case_defendant_detail=case_test["被告基本情况"],
            case_details=case_test["基本案情"],
            case_plaintiff_detail=case_test["原告诉请判令（公诉机关指控）"],
            case_type=case_test["类别"] + '案件',
            case_court_record=court_judge_analysis
            )
        #print(task_prompt)
        try:
            judge_analysis = GPT_4(judge_final_system, task_prompt)
            judge_final_result[case_test['案号']] = judge_analysis
            #print(judge_analysis)
        except:
            print('Error:', case_test['案号'])
            error_list.append(case_test['案号'])


        with open('judge_final_result.json', 'w', encoding='utf-8') as file:
            json.dump(judge_final_result, file, ensure_ascii=False, indent=4)

print(error_list)



    
