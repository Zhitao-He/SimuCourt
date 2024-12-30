from pyserini.search.lucene import LuceneSearcher
import json
from tqdm import tqdm 
import os 

def find_value_by_id_in_folder_with_progress(dict_path, target_id):
    
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if target_id in data:
            return data[target_id]  
    except json.JSONDecodeError as e:
        print(f"Error reading {file_path}: {e}")

    return None  

def case_searcher(case_type, case_details, case_cause):
    if len(case_details) > 2100:
        case_details = case_details[:2100]
    if case_type == '民事案件':
        searcher = LuceneSearcher('retrieve_index_data/index/index_civial')
    elif case_type == '刑事案件':
        searcher = LuceneSearcher('retrieve_index_data/index/index_criminal')
    elif case_type == '行政案件':
        searcher = LuceneSearcher('retrieve_index_data/index/index_administrative')

    searcher.set_language('zh')

    print(f"Searching for '{case_cause}'...")
    hits = searcher.search(case_details, 50) 
    top_hits_ids = [hits[i].docid for i in range(min(50, len(hits)))]
    return top_hits_ids  

def process_dataset(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    case_candidate_dict = {}
    case_candidate_type = {}
    case_candidate_type["民事案件"] = []
    case_candidate_type["刑事案件"] = []
    case_candidate_type["行政案件"] = []

    for idx, item in enumerate(data):
        
        # 一审
        case_number = item.get("案号", "")
        case_type = item.get("类别", "") + '案件'
        case_details = item.get("基本案情", "")
        case_cause = item.get("案由", "")
        case_judge = item.get("法院意见", "")
        # 二审
        case_details1 = item.get("一审法院认定事实", "")
        case_details2 = item.get("一审法院意见", "")
        case_details3 = item.get("本院二审查明事实", "")
        case_details4 = item.get("二审意见", "")
        case_details_all = case_details1 + case_details2 + case_details3 + case_details4

        print('Now {} processing: {}'.format(idx+1, case_number))
        top_hits_ids = case_searcher(case_type, case_details_all, case_cause)

        case_candidate_type[case_type].append([case_number, top_hits_ids])

    for case_type, case_list in case_candidate_type.items():
        if len(case_list) == 0:
            continue
        else:
            if case_type == '民事案件':
                dict_path = '民事案件/dict_civial.json'
            elif case_type == '刑事案件':
                dict_path = '刑事案件/dict_criminal.json'
            elif case_type == '行政案件':
                dict_path = '行政案件/dict_administrative.json'

            with open(dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print('Processing {}'.format(case_type))
            for case_ids in tqdm(case_list):
                case_number, top_hits_ids = case_ids[0], case_ids[1]
                candidate_case_list = []
                try:
                    for target_id in top_hits_ids:
                        case_data = data[target_id]
                        candidate_case_list.append(case_data)
                except json.JSONDecodeError as e:
                    print(f"Error reading {file_path}: {e}")

                case_candidate_dict[case_number] = candidate_case_list

    target_folder = 'retrieve_candi_case/all_dataset'
    case_candidate_dict_save_path = os.path.join(target_folder, 'case_candidate_dict(2).json')
    with open(case_candidate_dict_save_path, 'w', encoding='utf-8') as file:
        json.dump(case_candidate_dict, file, ensure_ascii=False, indent=4)
    
    return None

file_path = 'SimuCourt1.18(2).json'

processed_data = process_dataset(file_path)




