import json
import re

def parse_law_clause(clause):
    # 使用正则表达式匹配法律名称和条款编号
    law_name_match = re.search(r"《(.*?)》", clause)
    clause_number_match = re.search(r"第[\u4e00-\u9fa5\d]+条", clause)
    clause_part_match = re.search(r"第[\u4e00-\u9fa5\d]+款", clause)
    
    law_name = law_name_match.group(1) if law_name_match else None
    clause_number = clause_number_match.group(0) if clause_number_match else None
    if '款' not in clause:
        return law_name, clause_number, None
    else:
        clause_part = clause_part_match.group(0) if clause_part_match else None

        return law_name, clause_number, clause_part

def split_clause(clause):
    # 使用正则表达式匹配法律名称和条款编号
    law_name_match = re.search(r"(.+?)《(.+?)》", clause)
    clause_number_match = re.search(r"第[\u4e00-\u9fa5\d]+条", clause)

    if law_name_match and clause_number_match:
        law_name = law_name_match.group(0).replace("《", "〈").replace("》", "〉")
        clause_number = clause_number_match.group(0)
    else:
        law_name = None
        clause_number = None

    return law_name, clause_number

laws_base_path = 'all_laws.json'
with open(laws_base_path, 'r', encoding='utf-8') as file:
    laws_base = json.load(file)

candi_laws_path = 'case_number_candi_laws.json'
with open(candi_laws_path, 'r', encoding='utf-8') as file:
    candi_laws = json.load(file)

for k, candi_list in candi_laws.items():
    #print(k)
    for candi in candi_list:
        candi_laws_detiall_list = {}
        candi_laws_list = candi['审判依据']

        for law_clause in candi_laws_list:
            if law_clause.startswith("《"):
                law_name, clause_number, clause_part  = parse_law_clause(law_clause)
            else:
                law_name, clause_number = split_clause(law_clause)
            try:
                law_detial = laws_base[law_name][clause_number]
                if (law_detial in candi_laws_detiall_list.values()) and (law_detial != None):
                    continue
                else:
                    candi_laws_detiall_list[law_clause] = law_detial
                
            except:
                candi_laws_detiall_list[law_clause] = 'None'
        candi['审判依据'] = candi_laws_detiall_list

with open('case_laws_detail.json', 'w', encoding='utf-8') as file:
    json.dump(candi_laws, file, ensure_ascii=False, indent=4)
