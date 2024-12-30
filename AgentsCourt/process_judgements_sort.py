import pandas as pd
import os
import json
import re
import uuid

def remove_last_sentence(text):
    text = str(text)
    sentences = re.split('。|！|？', text)
    return '。'.join(sentences[:-1]) if sentences else text

def process_full_text(text):
    text = text.replace("&#xa0;", "")

    first_hao_index = text.find("号")
    return text[first_hao_index + 1:] if first_hao_index != -1 else text

def process_and_remove_last_sentence(text):
    text = str(text)

    text = text.replace("&#xa0;", "")

    first_hao_index = text.find("号")
    processed_text = text[first_hao_index + 1:] if first_hao_index != -1 else text

    sentences = re.split('。|！|？', processed_text)
    return '。'.join(sentences[:-1]) if sentences else processed_text

def process_csv(file_path, filename):
    df = pd.read_csv(file_path)
    
    allowed_types = ["刑事案件", "民事案件", "行政案件"]
    df_filtered = df[df['案件类型'].isin(allowed_types)].copy()  

    excluded_procedures = ['刑罚与执行变更', '特别程序', '其他', '督促', '非诉财产保全审查', '刑事审判监督', 
                        '催告', '执行实施', '第三人撤销之诉', '人身安全保护令', '强制医疗', 
                        'nan', '非诉证据保全审查', '非诉证据保全审查']
    df_filtered = df_filtered.copy()  
    df_filtered = df_filtered[~df_filtered['审理程序'].isin(excluded_procedures)]


    df_filtered.loc[:, '全文'] = df_filtered['全文'].apply(process_and_remove_last_sentence)

    columns_to_keep = ['案号', '案件名称', '案件类型', '审理程序', '案由', '全文']
    df_selected = df_filtered[columns_to_keep].copy()

    df_selected['unique_id'] = [str(uuid.uuid4()) for _ in range(len(df_selected))]
    
    df_selected = df_selected[df_selected['全文'].str.len() > 350]

    case_reason_counts = df_selected['案由'].value_counts()

    large_case_reasons = case_reason_counts[case_reason_counts > 1500].index

    for case_reason in large_case_reasons:
        df_case_reason = df_selected[df_selected['案由'] == case_reason]
        df_selected = df_selected[df_selected['案由'] != case_reason]  
        df_case_reason = df_case_reason.sort_values(by='全文', key=lambda x: x.str.len(), ascending=False).head(1500)
        df_selected = pd.concat([df_selected, df_case_reason], ignore_index=True)  

    data_dict = df_selected.to_dict(orient='records')

    print("Total records in data_dict:", len(data_dict))

    json_str = json.dumps(data_dict, ensure_ascii=False, indent=4)

    target_folder = 'SimuCourt'
    with open(os.path.join(target_folder  ,os.path.splitext(filename)[0] + '.json'), 'w', encoding='utf-8') as json_file:
        json_file.write(json_str)


def file_process(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            print('Now: ', filename)
            file_path = os.path.join(folder_path, filename)
            try:
                process_csv(file_path, filename)
            except:
                print('error: ', filename)

folder_path_ = 'SimuCourt'
file_process(folder_path_)
