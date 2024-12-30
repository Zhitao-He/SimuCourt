# -*- coding: utf-8 -*-
import json
from openai import OpenAI
from tqdm import tqdm 
import httpx


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def GPT_4(system_massage, prompt):
    #time.sleep(10)
    client = OpenAI(
        base_url="https://oneapi.xty.app/v1", 
        api_key="xxx",
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
    

# 数据集
case_dataset = 'SimuCourt1.18(2).json'
with open(case_dataset, 'r', encoding='utf-8') as file:
    case_data = json.load(file)

# 庭审记录
court_record_path = 'court_records(2).json'
with open(court_record_path, 'r', encoding='utf-8') as file:
    court_record = json.load(file)

# prompt
judge_analysis_record_path = '/system_prompt/judge_analysis_record2.txt'
with open(judge_analysis_record_path, "r") as f:
    judge_analysis_record_system = f.read()

judge_analysis_record_result = {}
error_list = []
error_case_list = []
for case_test in tqdm(case_data):
    
        # 庭审分析
        if case_test['案号'] in court_record:
            current_court_record = court_record[case_test['案号']]
            if len(current_court_record) >= 2:
                record1 = current_court_record[0]
                record2 = current_court_record[1]
                current_court_record_text = record1 + "\n" + record2
            else:
                current_court_record_text = current_court_record[0]
        else:
            current_court_record_text = '无'

        CASE_TEMPLATE = """
        你正在参与一次模拟二审法庭的活动，请记住这是一场虚拟的过程，你现在扮演一位专业的法官，请根据以下指引进行发言：

        请注意以下几点：
        1、若当前案件为**刑事案件**：则需要首先明确被告人的具体罪名和犯罪事实。评估犯罪行为对受害者及社会造成的影响和危害。考虑被告人的认罪态度、悔罪表现及犯罪后的改正行为。
        2、若当前案件为**民事案件**：则需要确立案件争议焦点，如合同违约、财产纠纷、侵权行为等。根据所提供的证据，评估各方责任大小和责任分配。确定适当的赔偿金额或其他补救措施，如返还财产、停止侵权行为等。
        3、若当前案件为**行政案件**：则需要分析涉案的行政行为是否符合法律法规的要求，是否超越了行政机关的权限。考虑行政行为对个人或组织的影响，是否有侵犯合法权益的情况。在判定行政行为不当或非法时，考虑适当的补救措施，如撤销行政决定、恢复原状、赔偿损失等。

        不管什么情况下，你的每一次发言只能且必须遵守以下格式：
        [法官分析]：本院认为，<你的分析>
        [审判依据]：综上所述，依照：<你依据的法律条文（陈列出案件涉及的法律条款具体名称如第几条第几款第几项）>
        [最终判决]：判决如下：<你的判决（必须给出判决结果，且不可包含除判决结果外的内容）>

        以下是一些案件的基本情况、庭审记录及最终判决结果：
        ###
        上诉人：（原审被告）：屈春雷
        被上诉人：（原审原告）：雷雨
        案件类型: 民事案件
        一审法院认定事实：2019年4月，原被告与雷磊达成口头合伙协议，以850000元的价格，从汪进军处转让榆林市榆阳区青柠影咖啡店,由原被告与雷磊合伙经营，其中原告雷雨占股50%，雷磊占股30%，被告屈春雷占股20%。2019年5月16日，榆林市榆阳区青柠影饮品店办理个体工商户登记，雷雨系经营者。2020年11月11日，榆林市榆阳区青柠影休闲吧办理个体工商户登记，屈春雷系经营者。2022年1月27日，原被告合伙结算，被告向原告出具借条两份，分别载明：“今借到雷雨人民币玖万零伍佰元整。”“今借到雷雨人民币贰万元整”。2022年1月31日，被告通过微信向原告妻子刘英英转账交付18000元；2022年2月21日，被告通过微信向原告妻子刘英英转账交付7000元。原被告就还款事宜协商无果，故成诉。
        一审法院意见：一审法院认为，当事人对自己提出的主张有责任提供证据予以证明。本案原告提供《借条》两份证明原被告之间形成借款事实，被告对《借条》真实性予以认可，但称借条载明的110500元系盈利后要给原告补偿的损失，本院经审查认为，被告作为完全民事行为能力人，自愿在原被告合伙结算后，向原告出具涉案借条，可以认定双方对合伙结算后的债务转化为民间借贷达成了合意，被告应当按照借条确定的金额履行还款义务。借条出具后，被告通过原告的妻子向原告转账偿还25000元，原告称该25000元系股权转让费，与本案借款无关，但举证期限内未提交证据予以佐证，应当由原告承担举证不能的法律后果，对该主张不予支持，对被告偿还的该25000元应当认定为偿还的涉案借款，予以扣除。原告主张除借条载明的110500元外，尚有10000元借款但被告未出具借条，被告不予认可，原告亦未能提交证据予以佐证，对该主张依法不予支持。原告主张从借条出具之日起，按照全国银行间同业拆借中心一年期贷款市场报价利率计算利息，但涉案借条上并未约定利息，原告亦未能提交证据证明双方口头约定了利息，依法应当视为不支付利息，故对原告的利息主张不予支持。
        一审法院审判依据：《中华人民共和国民法典》第六百七十五条、第六百八十条，《中华人民共和国民事诉讼法》第六十七条
        一审法院审判结果：一、被告屈春雷于本判决生效之日起十日内向原告雷雨偿还借款本金85500元；二、驳回原告其他诉讼请求。
        二审上诉请求：1、请求人民法院依法判令被告立即偿还原告借款120500元以及利息
        二审查明事实：二审中，当事人没有提交新证据。本院对一审查明的事实予以确认。
        二审庭审辩论：
        [上诉人请求]：我作为上诉人请求：1、请求依法撤销宝塔区人民法院2023陕06**民初6448号民事判决书，并将本案发回重审或依法改判。2、本案一审、二审诉讼费由被上诉人承担。事实与理由：一审认定事实清楚，适用法律错误。被上诉人所主张的借款根本不复存在，被上诉人也未向上诉人付过任何借款。该款项实际为前期被上诉人对于合伙期间收款收据保管不当造成的损失的分红补贴，原审法院以双方合伙结算为由认定为借款与事实不符。
        [被上诉人辩解]：我作为被上诉人辩解：上诉人称借据是给答辩人的分红补贴，系纯属子虚乌有，与事实不符，事实为双方在合伙期间发生的多笔借款，合伙结算后，上诉人出具的借据。上诉人陈述的出具借据后偿还的25000元系偿还借款本金110500元也系与事实不符，该两笔转账为股份转让款，且转让款尚欠10000元。在出具两张借据时，双方还对股份转让进行了结算，答辩人将股份作价50000元转让给上诉人，但只是口头约定，并未出具书面文件。
        最终裁决：
        [法官分析]：本院认为，上诉人屈春雷对于借条的真实性并无异议，但主张借条系因被上诉人雷雨对合伙期间收款收据保管不当造成损失的分红补贴，并非借款。而上诉人屈春雷作为完全民事行为能力人，应当预见出具借条所带来的的不利法律后果。在出具借条后，应当按照借条约定偿还借款。对于上诉人屈春雷要求被上诉人雷雨承担因服务器搬走，导致影咖不能正常影业所带来的的损失，与本案不属同一法律关系，可另案主张。综上所述，上诉人屈春雷的上诉请求不能成立，应予驳回。一审判决认定事实清楚，适用法律正确。
        [审判依据]：《中华人民共和国民事诉讼法》第一百七十七条第一款第（一）项
        [最终判决]：驳回上诉，维持原判。

        你将收到当前案件的一审基本情况、上诉人请求、法庭辩论，请根据你作为一名法官的专业知识进行最终的判决。
        不管什么情况，你必须在[最终判决]中给出如示例中的明确的判决结果！
        上诉人：{case_plaintiff}，上诉人基本情况：{case_defendant_detail}
        被上述人：{case_defendant}
        案件类型: {case_type}
        一审法院认定事实：{first_fact}
        一审法院意见：{first_analysis}
        一审法院审判依据：{first_laws}
        一审法院审判结果：{first_result}
        二审上诉请求：{second_appeal}
        二审查明事实：{second_fact}
        二审庭审辩论：{second_debate}
        最终裁决："""

        CASE_TEMPLATE1 = """
        你正在参与一次模拟二审法庭的活动，请记住这是一场虚拟的过程，你现在扮演一位专业的法官，请根据以下指引进行发言：

        请注意以下几点：
        1、若当前案件为**刑事案件**：则需要首先明确被告人的具体罪名和犯罪事实。评估犯罪行为对受害者及社会造成的影响和危害。考虑被告人的认罪态度、悔罪表现及犯罪后的改正行为。
        2、若当前案件为**民事案件**：则需要确立案件争议焦点，如合同违约、财产纠纷、侵权行为等。根据所提供的证据，评估各方责任大小和责任分配。确定适当的赔偿金额或其他补救措施，如返还财产、停止侵权行为等。
        3、若当前案件为**行政案件**：则需要分析涉案的行政行为是否符合法律法规的要求，是否超越了行政机关的权限。考虑行政行为对个人或组织的影响，是否有侵犯合法权益的情况。在判定行政行为不当或非法时，考虑适当的补救措施，如撤销行政决定、恢复原状、赔偿损失等。

        不管什么情况下，你的每一次发言只能且必须遵守以下格式：
        [法官分析]：本院认为，<你的分析>
        [审判依据]：综上所述，依照：<你依据的法律条文（陈列出案件涉及的法律条款具体名称如第几条第几款第几项）>
        [最终判决]：判决如下：<你的判决（必须给出判决结果，且不可包含除判决结果外的内容）>

        你将收到当前案件的一审基本情况、上诉人请求、法庭辩论，请根据你作为一名法官的专业知识进行最终的判决。
        不管什么情况，你必须在[最终判决]中给出如示例中的明确的判决结果！
        上诉人：{case_plaintiff}，上诉人基本情况：{case_defendant_detail}
        被上述人：{case_defendant}
        案件类型: {case_type}
        一审法院认定事实：{first_fact}
        一审法院意见：{first_analysis}
        一审法院审判依据：{first_laws}
        一审法院审判结果：{first_result}
        二审上诉请求：{second_appeal}
        二审查明事实：{second_fact}
        二审庭审辩论：{second_debate}
        最终裁决："""

        CASE_TEMPLATE2 = """
        你正在参与一次模拟二审法庭的活动，请记住这是一场虚拟的过程，你现在扮演一位专业的法官，请根据以下指引进行发言：

        请注意以下几点：
        1、若当前案件为**刑事案件**：则需要首先明确被告人的具体罪名和犯罪事实。评估犯罪行为对受害者及社会造成的影响和危害。考虑被告人的认罪态度、悔罪表现及犯罪后的改正行为。
        2、若当前案件为**民事案件**：则需要确立案件争议焦点，如合同违约、财产纠纷、侵权行为等。根据所提供的证据，评估各方责任大小和责任分配。确定适当的赔偿金额或其他补救措施，如返还财产、停止侵权行为等。
        3、若当前案件为**行政案件**：则需要分析涉案的行政行为是否符合法律法规的要求，是否超越了行政机关的权限。考虑行政行为对个人或组织的影响，是否有侵犯合法权益的情况。在判定行政行为不当或非法时，考虑适当的补救措施，如撤销行政决定、恢复原状、赔偿损失等。

        不管什么情况下，你的每一次发言只能且必须遵守以下格式：
        [法官分析]：本院认为，<你的分析>
        [审判依据]：综上所述，依照：<你依据的法律条文（陈列出案件涉及的法律条款具体名称如第几条第几款第几项）>
        [最终判决]：判决如下：<你的判决（必须给出判决结果，且不可包含除判决结果外的内容）>

        你将收到当前案件的一审基本情况、上诉人请求、法庭辩论，请根据你作为一名法官的专业知识进行最终的判决。
        不管什么情况，你必须在[最终判决]中给出如示例中的明确的判决结果！
        上诉人：{case_plaintiff}，上诉人基本情况：{case_defendant_detail}
        被上述人：{case_defendant}
        案件类型: {case_type}
        一审法院认定事实：{first_fact}
        一审法院意见：{first_analysis}
        一审法院审判依据：{first_laws}
        一审法院审判结果：{first_result}
        二审上诉请求：{second_appeal}
        二审查明事实：{second_fact}
        最终裁决："""

        # 基本案情
        task_prompt = CASE_TEMPLATE2.format(
            
            case_plaintiff=case_test["上诉人"], 
            case_defendant=case_test["被上诉人"],
            case_defendant_detail=case_test["上诉人基本情况"],
            case_type=case_test["类别"] + '案件',
            first_fact=case_test["一审法院认定事实"],
            first_analysis=case_test["一审法院意见"],
            first_laws=case_test["一审法院审判依据"],
            first_result=case_test["一审法院审判结果"],
            second_appeal=case_test["上诉请求"],
            second_fact=case_test["本院二审查明事实"]
            )
        
        #print(task_prompt)
        try:
            judge_self_analysis = GPT_4(judge_analysis_record_system, task_prompt)
            judge_analysis_record_result[case_test['案号']] = judge_self_analysis
            #print(judge_analysis)
        except:
            print('Error:', case_test['案号'])
            error_list.append(case_test['案号'])

        with open('record.json', 'w', encoding='utf-8') as file:
            json.dump(judge_analysis_record_result, file, ensure_ascii=False, indent=4)

print(error_list)



    
