# -*- coding: utf-8 -*-
import json
from openai import OpenAI
from tqdm import tqdm 
#from transformers import AutoTokenizer
import tiktoken
client = OpenAI(api_key='')


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def GPT_4(prompt):
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        #model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": '你是一个专业的法律助手'}, 
                    {"role": "user", "content": prompt}]
    )
    #print(response)
    return response.choices[0].message.content.strip()
    

candidate_dict = "reranked_candidates.json"
with open(candidate_dict, "r", encoding="utf-8") as file:
    data = json.load(file)


error_candidate_list = []
case_number_candi_laws = {}
error_case_number = []
for case_number, candidate_list in tqdm(data.items()):
    #if case_number in error_candidate_list:
        laws_dict = []
        i = 0
        for candidate in candidate_list:
            if i < 3:
                
                candidate_document = candidate["全文"]
                candidate_type = candidate["案件类型"]
                candidate_number = candidate["案号"]

                candidate_document_len = num_tokens_from_string(candidate_document, "gpt-3.5-turbo")
                # 找到“本院认为”
                # 查找子字符串"本院认为"首次出现的位置
                if "本院认为" in candidate_document:
                    index_judge = candidate_document.find("本院认为")
                    if index_judge != -1:
                        # 去除"本院认为"之前的文本
                        candidate_document = candidate_document[index_judge:]
                        print("捕获关键词'本院认为'...")
                else:
                    if candidate_document_len <= 7000:
                        # 如果超过8000个字符，去除前一半的字符
                        candidate_document = candidate_document
                    elif 7000 < candidate_document_len <= 10000:
                        candidate_document = candidate_document[len(candidate_document)//2:]
                    else:
                        candidate_document = candidate_document[-6000:]

                # 1、加载刑事、民事（行政）案件的prompt
                if candidate_type == "刑事案件":
                    template_path = "/system_prompt/crimial_extract_prompt.txt"
                    with open(template_path, "r") as f:
                        template = f.read()
                    prompt_form = """抽取结果:<result_initial>
                    请将以上内容整理为以下格式: 
                    抽取结果:{"审判依据":["《中华人民共和国刑法》第一百三十三条之一第一款第(二)项","《中华人民共和国刑法》第六十七条第一款", "《中华人民共和国刑法》第七十二条第一款", "《中华人民共和国刑法》第七十二条第三款"，"《中华人民共和国刑法》第七十三条第一款"，"《中华人民共和国刑法》第七十三条第三款"], "审判结果":{"罪名":"被告人金某某犯危险驾驶罪","刑期":"判处拘役二个月，缓刑二个月","罚金":"罚金人民币四千元"}}
                    抽取结果:
                    """
                else:
                    template_path = "/system_prompt/civial_extract_prompt.txt"
                    with open(template_path, "r") as f:
                        template = f.read()
                    prompt_form = """抽取结果:<result_initial>
                    请将以上内容整理为以下格式: 
                    抽取结果:{"审判依据": ["《中华人民共和国行政诉讼法》第七十条第（一）项", "《中华人民共和国公司法》第六条", "《中华人民共和国公司登记管理条例》第四条","《中华人民共和国公司登记管理条例》第八条"、"《中华人民共和国公司登记管理条例》第九条"、"《中华人民共和国公司登记管理条例》第二十条", "《中华人民共和国行政许可法》第三十一条"、"《中华人民共和国行政许可法》第六十九条", "《企业登记程序规定》第三条"、"《企业登记程序规定》第八条"], "审判结果": {"结果1": "撤销被告济南市历下区市场监督管理局注册登记原告彭某某为济南某某公司监事的行政行为", "结果2": "案件受理费人民币五十元，由被告济南市历下区市场监督管理局负担"}}
                    抽取结果:
                    """
                prompt_extract = template.replace("<case_detail>", candidate_document)
                print("Extracting...")
                
                try:
                    result_initial = GPT_4(prompt_extract)
                    dictionary = json.loads(result_initial)
                    print("Right form. Next...")
                    dictionary["案号"] = candidate_number
                    dictionary["案件类型"] = candidate_type
                    dictionary["content"] = candidate_document
                    laws_dict.append(dictionary)
                except json.JSONDecodeError:
                    try:
                        print("Revising...")
                        prompt_revise = prompt_form.replace("<result_initial>", result_initial)
                        #print("prompt_revise:", prompt_revise)
                        
                        result_reform = GPT_4(prompt_revise)
                        print("result_reform:", result_reform)
                    
                        dictionary = json.loads(result_reform)
                        print("Revisd!")
                        dictionary["案号"] = candidate_number
                        dictionary["案件类型"] = candidate_type
                        dictionary["content"] = candidate_document
                        laws_dict.append(dictionary)
                    except json.JSONDecodeError:
                        # 如果转换失败，则抛出错误
                        error_case_number.append(case_number)
                        print("Error {}".format(candidate_number))
                
                i += 1
            
        case_number_candi_laws[case_number] = laws_dict

        with open("case_number_candi_laws.json", "w", encoding="utf-8") as file:
            json.dump(case_number_candi_laws, file, ensure_ascii=False, indent=4)

print(error_case_number)






