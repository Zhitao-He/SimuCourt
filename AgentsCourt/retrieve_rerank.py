from FlagEmbedding import FlagModel
import os
import json
from tqdm import tqdm
os.environ["CUDA_VISIBLE_DEVICES"]="9"

def document_split(cadidate_cases):
    id_document_list = []
    for entry in cadidate_cases:
        processed_entry = {
            "id": entry["unique_id"],  
            "contents": entry["全文"] 
        }

        if len(processed_entry["contents"]) > 500:
            full_texts = [processed_entry["contents"][i:i+500] for i in range(0, len(processed_entry["contents"]), 500)]
            for part in full_texts:
                if len(part) < 100:
                    continue
                else:
                    new_entry = {"id": processed_entry["id"], "contents": part}
                    id_document_list.append(new_entry)
        else:
            id_document_list.append(processed_entry)
    return id_document_list

def rerank_by_bge(query, id_document_list):
    queries = [query]
    
    document_list = [li["contents"] for li in id_document_list]
    id_list = [li["id"] for li in id_document_list]
    
    q_embeddings = model.encode_queries(queries)
    p_embeddings = model.encode(document_list)
    scores = q_embeddings @ p_embeddings.T

    # 输出排序后的id
    paired_list = list(zip(id_list, scores[0]))
    sorted_paired_list = sorted(paired_list, key=lambda x: x[1], reverse=True)
    sorted_id_list = [id for id, score in sorted_paired_list]
    # 保留每个ID的最靠前的index
    unique_ids = []
    for id in sorted_id_list:
        if id not in unique_ids:
            unique_ids.append(id)


    return unique_ids

def rerank_candidate(unique_ids, candidate_cases):
    reranked_candidates = []
    for id in unique_ids:
        for case in candidate_cases:
            if case["unique_id"] == id:
                reranked_candidates.append(case)
                break
    return reranked_candidates
    
model = FlagModel('BAAI/bge-large-zh-v1.5', 
                  query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                  use_fp16=True) 

candidate_file_path = 'retrieve_candi_case/all_dataset/case_candidate_dict(2).json'
with open(candidate_file_path, 'r', encoding='utf-8') as candidate_file:
    cadidate_data = json.load(candidate_file)

case_file_path = 'SimuCourt1.18(2).json'
with open(case_file_path, 'r', encoding='utf-8') as case_file:
    case_data = json.load(case_file)

reranked_candidates = {}
for case in tqdm(case_data):
    case_id = case["案号"]

    case_details1 = case.get("一审法院认定事实", "")
    case_details2 = case.get("一审法院意见", "")
    case_details3 = case.get("本院二审查明事实", "")
    case_details4 = case.get("二审意见", "")
    case_details_all = case_details1 + case_details2 + case_details3 + case_details4
    if len(case_details_all) > 2100:
        case_details_all = case_details_all[:2100]

    candidate_cases = cadidate_data[case_id]

    id_document_list = document_split(candidate_cases)
    unique_ids = rerank_by_bge(case_details_all, id_document_list)
    reranked_list = rerank_candidate(unique_ids, candidate_cases)
    reranked_candidates[case_id] = reranked_list

with open("retrieve_candi_case/all_dataset/reranked_candidates.json", "w", encoding='utf-8') as file:
    json.dump(reranked_candidates, file, ensure_ascii=False, indent=4)

