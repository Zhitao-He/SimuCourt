import json

def remove_special_characters(law_list):
    cleaned_list = []
    for law in law_list:
        cleaned_law = law.replace("（", "").replace("）", "").replace("(", "").replace(")", "").replace("《", "").replace("》", "").replace("<", "").replace(">", "").replace("〈", "").replace("〉", "")
        cleaned_list.append(cleaned_law)
    return cleaned_list

def calculate_legal_text_metrics(gold_list, pred_list):
    cleaned_gold_list = remove_special_characters(gold_list)
    cleaned_pred_list = remove_special_characters(pred_list)
    tp = len(set(cleaned_gold_list).intersection(set(cleaned_pred_list)))
    fp = len(cleaned_pred_list) - tp
    fn = len(cleaned_gold_list) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return precision, recall, f1

def calculate_single_metrics(gold_list, pred_list):
    cleaned_gold_list = remove_special_characters(gold_list)
    cleaned_pred_list = remove_special_characters(pred_list)

    tp = len(set(cleaned_gold_list).intersection(set(cleaned_pred_list)))
    fp = len(cleaned_pred_list) - tp
    fn = len(cleaned_gold_list) - tp

    return tp, fp, fn

gold_judge_path = 'judge_result.json'
with open(gold_judge_path, 'r', encoding='utf-8') as file:
    gold_judge = json.load(file)

GPT4_path = 'refine_eval.json'
with open(GPT4_path, 'r', encoding='utf-8') as file:
    model_judge = json.load(file)

total_tp = total_fp = total_fn = 0

for number, gold_result in gold_judge.items():
            pred_result = model_judge[number]

            gold_law_list = gold_result["审判依据"]
            pred_law_list = pred_result["审判依据"]

            tp, fp, fn = calculate_single_metrics(gold_law_list, pred_law_list)
            # 累加到总数
            total_tp += tp
            total_fp += fp
            total_fn += fn

precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print('all_precision', precision)
print('all_recall', recall)
print('all_f1', f1)
print('=====================================')

total_tp_x = total_fp_x = total_fn_x = 0

for number, gold_result in gold_judge.items():
    #if number in model_judge:
        if gold_result["案件类型"] == '刑事案件':
            #print('number:', number)
            pred_result = model_judge[number]

            gold_law_list = gold_result["审判依据"]
            pred_law_list = pred_result["审判依据"]

            tp, fp, fn = calculate_single_metrics(gold_law_list, pred_law_list)
            # 累加到总数
            total_tp_x += tp
            total_fp_x += fp
            total_fn_x += fn


precision = total_tp_x / (total_tp_x + total_fp_x) if (total_tp_x + total_fp_x) > 0 else 0
recall = total_tp_x / (total_tp_x + total_fn_x) if (total_tp_x + total_fn_x) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print('X_precision', precision)
print('X_recall', recall)
print('X_f1', f1)
print('=====================================')

total_tp_m = total_fp_m = total_fn_m = 0

for number, gold_result in gold_judge.items():
    #if number in model_judge:
        if gold_result["案件类型"] == '民事案件':
            #print('number:', number)
            pred_result = model_judge[number]

            gold_law_list = gold_result["审判依据"]
            pred_law_list = pred_result["审判依据"]

            tp, fp, fn = calculate_single_metrics(gold_law_list, pred_law_list)
            # 累加到总数
            total_tp_m += tp
            total_fp_m += fp
            total_fn_m += fn

precision = total_tp_m / (total_tp_m + total_fp_m) if (total_tp_m + total_fp_m) > 0 else 0
recall = total_tp_m / (total_tp_m + total_fn_m) if (total_tp_m + total_fn_m) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print('m_precision', precision)
print('m_recall', recall)
print('m_f1', f1)
print('=====================================')

total_tp_z = total_fp_z = total_fn_z = 0

for number, gold_result in gold_judge.items():
        if gold_result["案件类型"] == '行政案件':
            #print('number:', number)
            pred_result = model_judge[number]

            gold_law_list = gold_result["审判依据"]
            pred_law_list = pred_result["审判依据"]

            tp, fp, fn = calculate_single_metrics(gold_law_list, pred_law_list)
            # 累加到总数
            total_tp_z += tp
            total_fp_z += fp
            total_fn_z += fn

precision = total_tp_z / (total_tp_z + total_fp_z) if (total_tp_z + total_fp_z) > 0 else 0
recall = total_tp_z / (total_tp_z + total_fn_z) if (total_tp_z + total_fn_z) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print('z_precision', precision)
print('z_recall', recall)
print('z_f1', f1)
