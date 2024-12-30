import json

# 数据集的gold result
gold_judge_path = 'judge_result.json'
with open(gold_judge_path, 'r', encoding='utf-8') as file:
    gold_judge = json.load(file)

# 输出结果
model_judge_path = 'refine_eval.json'
with open(model_judge_path, 'r', encoding='utf-8') as file:
    model_judge = json.load(file)

total_num = total_name = total_sentence = total_fine = 0

for number, gold_result in gold_judge.items():
    #print(number)
    if gold_result["案件类型"] == '刑事案件':
        total_num += 1
        pred_result = model_judge[number]

        gold_name = gold_result.get('罪名')
        gold_sentence = gold_result.get('刑期')
        gold_fine = gold_result.get('罚金')

        pred_name = pred_result["判决结果"].get('罪名')
        pred_sentence = pred_result["判决结果"].get('刑期')
        pred_fine = pred_result["判决结果"].get('罚金')

        

        if gold_name == pred_name:
            total_name += 1
        if gold_sentence == pred_sentence:
            total_sentence += 1
        if gold_fine == pred_fine:
            total_fine += 1
        
total_name_p = total_name/total_num
total_sentence_p = total_sentence/total_num
total_fine_p = total_fine/total_num


print('total_name', total_name_p)
print('total_sentence', total_sentence_p)
print('total_fine', total_fine_p)
