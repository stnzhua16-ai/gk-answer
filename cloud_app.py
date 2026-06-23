"""
国库知识答题助手 - 云部署版（与沙箱版完全同步）
"""
import json, re, os
import requests as req
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
API_BASE = "http://activity.njsummer.cn/aliredpack2nd"
DEFAULT_KEY = "eeeddc4f487b4bf7b0c9f1dad5d1ff99"

KB_DATA = [{"t": "国库机构按照什么体制设立？", "a": "C", "d": "《中华人民共和国国家金库条例》规定，国库机构按照国家财政管理体制设立。", "ct": "财政管理体制"}, {"t": "原则上一级财政应设立几级国库？", "a": "A", "d": "《中华人民共和国国家金库条例》规定，原则上一级财政设立一级国库。", "ct": "一级"}, {"t": "中国人民银行具体（）国库。组织管理国库工作是人民银行的一项重要职责。", "a": "A", "d": "《中华人民共和国国家金库条例》规定，中国人民银行具体经理国库", "ct": "经理"}, {"t": "凡代理国库业务和办理国库经收业务的商业银行、信用社均应设立哪个一级会计科目？", "a": "C", "d": "《商业银行、信用社代理国库业务管理办法》规定，应统一设立\"待结算财政款项\"一级科目。", "ct": "待结算财政款项"}, {"t": "《中华人民共和国国家金库条例》的颁布时间为（）。", "a": "A", "d": "《中华人民共和国国家金库条例》于1985年7月27日颁布实施。", "ct": "1985年7月27日"}, {"t": "国库经收处是否可以办理预算收入退付？", "a": "C", "d": "《商业银行、信用社代理国库业务管理办法》规定，国库经收处不得办理预算收入退付。", "ct": "不得办理"}, {"t": "代理支库的国库主任由谁兼任？", "a": "C", "d": "《商业银行、信用社代理国库业务管理办法》规定，代理支库的国库主任由代理行行长兼任。", "ct": "代理行行长"}, {"t": "商业银行、信用社有（）行为，情节严重的，不属于依照《中华人民共和国中国人民银行法》第四十六条的规定给予处罚的？", "a": "D", "d": "商业银行、信用社有下列行为之一，情节严重的，依照《中华人民共和国中国人民银行法》第四十六条的规定给予处罚：（一）不按规定设置“待结算财政款项”", "ct": "商业银行信用社占压挪用所收纳预算收入款项的"}, {"t": "代理支库的商业银行以及办理国库经收业务的商业银行和信用社，不得违规为征收机关开立什么账户？", "a": "C", "d": "《商业银行、信用社代理国库业务管理办法》规定，严禁违规为征收机关开立预算收入过渡账户。", "ct": "预算收入过渡账户"}, {"t": "国库经收处将经收税款转入\"待结算财政款项\"以外其他科目或账户的，视同什么行为处理？", "a": "B", "d": "根据《商业银行、信用社代理国库业务管理办法》，转入其他科目或账户视同挪用预算收入处理。", "ct": "挪用预算收入"}, {"t": "组织管理国库工作是（）的一项重要职责。", "a": "C", "d": "《中华人民共和国国家金库条例》规定，组织管理国库工作是人民银行的一项重要职责。", "ct": "人民银行"}, {"t": "商业银行、信用社申请代理支库业务的，申请人原则上为（）。", "a": "B", "d": "《商业银行、信用社代理支库业务审批管理办法》规定，申请人原则上为拟具体承办代理支库业务的商业银行、信用社或其分支机构。", "ct": "拟具体承办代理支库业务的商业银行信用社或其分支机构"}, {"t": "关于国库机构，以下哪项是错误的？", "a": "C", "d": "《中华人民共和国国家金库条例》规定，省辖市、自治州设立中心支库。", "ct": "省辖市自治州设立分库"}, {"t": "商业银行未经中国人民银行及其分支机构资格认定，擅自从事或变相从事国库集中收付业务的，中国人民银行及其分支机构应当责令改正，并依据（）进行处罚？", "a": "A", "d": "《国库集中收付代理银行资格认定管理办法》规定，擅自从事国库集中收付业务的，依据《中国人民银行法》第四十六条处罚。", "ct": "中华人民共和国中国人民银行法第四十六条"}, {"t": "国库集中收付代理银行应当履行的职责不包括以下哪项？", "a": "D", "d": "《国库集中收付代理银行资格认定管理办法》规定的职责中，不包括按季度报送分析报告的要求。", "ct": "每季度向同级财政部门报送国库集中收付业务开展情况分析报告"}, {"t": "《商业银行、信用社代理支库业务审批管理办法》规定，经准予代理支库业务的商业银行、信用社凭准予行政许可决定书，与初审行签订（）。", "a": "B", "d": "《商业银行、信用社代理支库业务审批管理办法》规定，凭准予行政许可决定书与初审行签订\"代理支库业务协议书\"。", "ct": "代理支库业务协议书"}, {"t": "同一税务机关在国库可以开设几个\"待缴库税款\"专户？", "a": "C", "d": "《待缴库税款收缴管理办法》规定，同一税务机关在国库只能设置一个\"待缴库税款\"专户。", "ct": "只能设置一个"}, {"t": "国库的主要权限不包括以下哪项？", "a": "D", "d": "《中华人民共和国国家金库条例》规定，国库的主要权限包括：任何单位和个人强令国库办理违反国家规定的事项，国库有权拒绝执行，并及时向上级报告。", "ct": "任何单位和个人强令国库办理违反国家规定的事项国库有权拒绝执行并及时向同级财政部门报告"}, {"t": "根据《关于跨境税费缴库退库业务管理有关事项的通知》，跨境税费缴库业务中，经收跨境外币税费的国库经收处必须具备什么资格？", "a": "B", "d": "跨境税费缴库业务中，经收跨境外币税费的国库经收处必须具备结售汇业务资格。", "ct": "结售汇业务资格"}, {"t": "各级国库库款的支拨，必须在同级财政存款余额内支付，（）。", "a": "C", "d": "《国库会计管理基本规定》规定，库款支拨只办理转账，不支付现金。", "ct": "只办理转账不支付现金"}, {"t": "跨境税费缴库可采用TIPS电子缴库方式，其前提是国库经收处的业务系统必须满足什么条件？", "a": "B", "d": "采用TIPS方式办理跨境税费缴库，国库经收处的业务系统必须接入国库信息处理系统（TIPS）。", "ct": "接入国库信息处理系统tips"}, {"t": "新中国最早发行的国债是（）。", "a": "A", "d": "新中国最早发行的国债是1949年12月发行的人民胜利折实公债。", "ct": "1949年12月发行的人民胜利折实公债"}, {"t": "国库应当按（）设置总账，按有关规定和要求设置相应分户账。", "a": "A", "d": "《国库会计管理基本规定》规定，国库应当按会计科目设置总账，按有关规定和要求设置相应分户账，根据国库会计核算需要设置相应的登记簿（表）。", "ct": "会计科目"}, {"t": "储蓄国债（电子式）的付息方式是（）。", "a": "A", "d": "储蓄国债（电子式）按年付息，最后一次利息随本金一起支付。", "ct": "每年付息一次息随本清"}, {"t": "关于储蓄国债（凭证式）收款凭证的管理，下列说法正确的是（）。", "a": "B", "d": "储蓄国债（凭证式）收款凭证记名，可以挂失，但不得更名或流通转让。", "ct": "记名可以挂失但不得更名或流通转让"}, {"t": "商业银行参与国库现金管理时，存款银行应设置（）一级负债类科目，科目下按国库级次分设账户，分别核算存入、归还中央和地方财政的国库定期存款。", "a": "B", "d": "《地方国库现金管理试点办法》规定，存款银行应设置“国库定期存款”一级负债类科目，科目下按国库级次分设账户，分别核算存入、归还中央和地方财政的国库定期存款。", "ct": "国库定期存款"}, {"t": "商业银行参与中央和地方国库现金管理时，国债、地方政府债券、政策性金融债券分别按（）比例进行质押。", "a": "D", "d": "《关于加强国库现金管理商业银行定期存款质押品管理有关事宜的通知》规定，商业银行参与中央和地方国库现金管理时，国债、地方政府债券、政策性金融债券分别按105%、110%、110%比例进行质押。", "ct": "105%110%110%"}, {"t": "地方国库现金管理操作工具为商业银行定期存款，定期存款期限在（）年期以内。", "a": "A", "d": "《地方国库现金管理试点办法》规定，地方国库现金管理操作工具为商业银行定期存款，定期存款期限在1年期以内。", "ct": "1"}, {"t": "关于“国库集中支付款项”科目的使用错误的是：（）", "a": "C", "d": "《关于规范商业银行、信用社代理国库相关业务使用会计科目的通知》规定“国库集中支付款项”科目，用于核算财政部门、预算单位零余额账户集中支付的款项。本科目为负债类科目，收到款项时，借记有关科目，贷记本科目", "ct": "本科目为资产类科目"}, {"t": "关于“国库集中收缴款项”科目的使用错误的是：（）", "a": "B", "d": "《关于规范商业银行、信用社代理国库相关业务使用会计科目的通知》规定：商业银行、信用社代理国库集中收付，应当设置“国库集中收缴款项”“国库集中支付款项”一级会计科目。“国库集中收缴款项”科目，用于核算存", "ct": "款项划缴国库时借记有关科目贷记本科目"}, {"t": "国库经收处在收纳预算收入时，应对缴款书的哪些内容进行认真审核？", "a": "ABCD", "d": "《商业银行、信用社代理国库业务管理办法》规定，国库经收处应对缴款书的上述各项要素进行全面审核。", "ct": "预算级次预算科目征收机关和指定收款国库等要素是否填写清楚|大小写金额是否相符字迹有无涂改|纳税人名称账号开户银行填写是否正确齐全|印章是否齐全清晰与预留印鉴是否相符"}, {"t": "凡代理国库业务和办理国库经收业务的商业银行、信用社，以下做法正确的有？", "a": "ABD", "d": "根据《商业银行、信用社代理国库业务管理办法》，严禁将预算收入转入\"待结算财政款项\"以外的其他科目。", "ct": "设立待结算财政款项一级科目|使用待报解预算收入专户核算收纳的预算收入|不得将预算收入转入其他科目"}, {"t": "关于国库经收处收纳预算收入的报解时限，下列说法正确的有？", "a": "ABC", "d": "《商业银行、信用社代理国库业务管理办法》规定，应于当日报解，当日不能报解的必须在下一个工作日报解，严禁延解占压。", "ct": "应在收纳当日办理报解入库手续|不得延解占压和挪用|如当日确实不能报解的必须在下一个工作日报解"}, {"t": "商业银行申请代理支库业务时，其经营合规稳健方面要求申请时前2年内无（  ）等影响代理支库业务审批的事项。", "a": "BCD", "d": "根据《商业银行、信用社代理支库业务审批管理办法》，经营合规稳健方面要求申请时前2年内无重大违法违规行为、被采取限制业务活动、被责令停业整顿、被接管等影响代理支库业务审批的事项。", "ct": "被采取限制业务活动|被责令停业整顿被接管|重大违法违规行为"}, {"t": "代理银行在代理国库集中收付业务期间，出现下列（ ）情形且情节严重的，中国人民银行及其分支机构将依据《中华人民共和国中国人民银行法》第四十六条进行处罚？", "a": "ABD", "d": "根据《国库集中收付代理银行资格认定管理办法》，代理银行在代理国库集中收付业务期间，有下列情形之一且情节严重的，中国人民银行及其分支机构依据《中华人民共和国中国人民银行法》第四十六条进行处罚：（一）未按", "ct": "未按规定设置使用国库集中收付会计科目和账户|未按规定支付国库集中支付资金|违规垫款"}, {"t": "以下关于申请国库集中收付代理银行资格的机构应具备的条件，哪些说法正确？（）", "a": "BC", "d": "《国库集中收付代理银行资格认定管理办法》规定，申请机构须存续2年以上且前2年内无重大违法违规行为，A、D两项年限不符。", "ct": "资产负债状况良好经营业绩和风险控制能力较强具备办理国库集中收付业务所需的技术条件|机构网点数量和分布能够满足代理业务需要人员配备能够满足代理业务需要"}, {"t": "代理银行在代理国库集中收付业务期间，下列（）情形属于占压财政资金行为？", "a": "BC", "d": "《国库集中收付代理银行资格认定管理办法》规定，未按规定及时将退回资金退回国库等构成占压财政资金。A、D均为合规操作。", "ct": "在收到国库集中支付退回资金的下两个工作日将资金退回国库|集中于月末处理国库集中支付退回资金"}, {"t": "跨境税费通过TIPS方式缴库，汇款用途（附言）必须注明的信息包括以下哪项？", "a": "ABC", "d": "根据《中国人民银行财政部国家税务总局关于跨境税费缴库退库业务管理有关事项的通知》，通过TIPS方式缴库，汇款用途须注明纳税人识别号、银行端查询缴税凭证序号和征收机关代码，不包括预算科目代码。", "ct": "纳税人识别号|银行端查询缴税凭证序号|征收机关代码"}, {"t": "目前我国储蓄国债的主要品种是（）。", "a": "AB", "d": "目前我国储蓄国债主要包括储蓄国债（电子式）和储蓄国债（凭证式）两个品种。", "ct": "储蓄国债电子式|储蓄国债凭证式"}, {"t": "与其他金融投资产品相比，储蓄国债的主要优点包括（）。", "a": "ABCD", "d": "储蓄国债具有信用等级高、安全性好、变现灵活、收益相对较高、购买方便等优点。", "ct": "信用等级高安全性好|变现灵活流动性好|到期实际收益通常高于国有大行相同期限储蓄存款的收益|发售网点多购买较为方便"}, {"t": "参与中央和地方国库现金管理的商业银行取得定期存款，可以使用（）作为质押品。", "a": "ABC", "d": "根据《关于加强国库现金管理商业银行定期存款质押品管理有关事宜的通知》，可用于质押的包括记账式国债、地方政府债券和政策性金融债券。", "ct": "记账式国债|地方政府债券|政策性金融债券"}, {"t": "商业银行参与地方国库现金管理时，存款银行收款后，应向地方财政部门开具存款单，载明（）等要素。", "a": "ABCD", "d": "《地方国库现金管理试点办法》第十七条规定，存款单应载明存款银行名称、存款金额、利率、期限等要素。", "ct": "存款银行名称|存款金额|利率|期限"}, {"t": "《关于规范商业银行、信用社代理国库相关业务使用会计科目的通知》规定：商业银行、信用社代理国库经收处业务，应当在\"待结算财政款项\"科目用于核算商业银行、信用社作为国库经收处收纳的、待报解国库的各项预算收入，包括：（）。", "a": "ABC", "d": "\"待结算财政款项\"科目核算范围包括税收收入、非税收入和社会保险费等预算收入。", "ct": "税收收入|非税收入|社会保险费"}, {"t": "《国家金库条例》规定：国家各项预算收入，分别由各级（）负责管理，并监督缴入国库。", "a": "ABC", "d": "《国家金库条例》规定，国家各项预算收入由各级财政机关、税务机关和海关负责管理并监督缴入国库。", "ct": "财政机关|税务机关|海关"}, {"t": "《国家金库条例》规定国库的基本职责，下列哪些选项是正确的：（）", "a": "ABD", "d": "《国家金库条例》规定，国库的基本职责包括向上级国库和同级财政机关反映预算收支执行情况，而非上级财政机关，ABD选项均为正确。", "ct": "办理国家预算收入的收纳划分和留解|办理国家预算支出的拨付|协助财政税务机关督促企业和其他有经济收入的单位及时向国家缴纳应缴款项对于屡催不缴的应依照税法协助扣收入库"}, {"t": "经收预算收入的商业银行分支机构和信用社均为国库经收处。（）", "a": "A", "d": "《商业银行、信用社代理国库业务管理办法》规定，经收预算收入的商业银行分支机构和信用社均为国库经收处。", "ct": ""}, {"t": "国库经收处收纳的预算收入属代收性质，不是正式入库。（）", "a": "A", "d": "《商业银行、信用社代理国库业务管理办法》规定，国库经收处收纳的预算收入属代收性质，不是正式入库。", "ct": ""}, {"t": "国库是国家金库的简称，负责办理国家预算资金的收入和支出。（）", "a": "A", "d": "《中华人民共和国国家金库条例》规定，国家金库简称国库，负责办理国家预算资金的收入和支出。", "ct": ""}, {"t": "国库业务工作实行垂直领导。各省、自治区、直辖市分库及其所属各级支库，既是中央国库的分支机构，也是地方国库。（）", "a": "A", "d": "《中华人民共和国国家金库条例》规定，国库业务工作实行垂直领导。各省、自治区、直辖市分库及其所属各级支库，既是中央国库的分支机构，也是地方国库。", "ct": ""}, {"t": "国家的一切预算收入，应按照规定全部缴入国库，地方政府机构也可代为保管。（）", "a": "B", "d": "《中华人民共和国国家金库条例》规定，国家的一切预算收入，应按照规定全部缴入国库，任何单位不得截留、坐支或自行保管。", "ct": ""}, {"t": "国库集中收付代理银行资格认定有效期为5年，代理银行在期满后拟延续资格认定有效期的，应当在期满6个月前申请延续。（ ）", "a": "A", "d": "《国库集中收付代理银行资格认定管理办法》规定，资格认定有效期为5年，延续申请须提前6个月提出。", "ct": ""}, {"t": "对于不符合国家预算、不符合国家有关财经制度的预算资金收支业务，各级国库部门有权拒绝办理。（）", "a": "A", "d": "《中华人民共和国国家金库条例》规定，对于不符合国家预算、不符合国家有关财经制度的预算资金收支业务，各级国库部门有权拒绝办理。", "ct": ""}, {"t": "各级国库应当设立专门的工作机构办理国库业务。（）", "a": "A", "d": "《中华人民共和国国家金库条例》规定，各级国库应当设立专门的工作机构办理国库业务。", "ct": ""}, {"t": "机构投资者可以购买储蓄国债（电子式）。（）", "a": "B", "d": "储蓄国债（电子式）仅面向个人投资者发行，机构投资者不能购买。", "ct": ""}, {"t": "储蓄国债可以上市流通转让。（）", "a": "B", "d": "储蓄国债不可上市流通转让，但可通过提前兑付和质押贷款方式变现。", "ct": ""}, {"t": "国库收纳库款以人民币为主，外币为辅。（）", "a": "B", "d": "《中华人民共和国国家金库条例》规定，国库收纳库款以人民币为限。以金银、外币等缴款，应当向当地银行兑换成人民币后缴纳。", "ct": ""}, {"t": "参与中央和地方国库现金管理的商业银行取得定期存款，可以使用已部分还本的债券作为质押品。（）", "a": "B", "d": "已部分还本的债券不得作为国库现金管理定期存款的质押品。", "ct": ""}, {"t": "政府的全部收入应当上缴财政专户，任何部门、单位和个人不得截留、占用、挪用或者拖欠。（）", "a": "B", "d": "《中华人民共和国预算法》规定，政府的全部收入应当上缴国家金库，任何部门、单位和个人不得截留、占用、挪用或者拖欠。", "ct": ""}, {"t": "商业银行、信用社占压、挪用所收纳预算收入款项的，情节严重的，依据《金融违法行为处罚办法》第二十二条的规定给予处罚。（）", "a": "B", "d": "商业银行、信用社占压、挪用所收纳预算收入款项的，依据《金融违法行为处罚办法》第二十二条的规定给予处罚。（无情节严重要求）", "ct": ""}, {"t": "国家实行国库集中收缴和集中支付制度，对政府全部收入和支出实行国库集中收付管理。（）", "a": "A", "d": "《中华人民共和国预算法》规定，国家实行国库集中收缴和集中支付制度，对政府全部收入和支出实行国库集中收付管理。", "ct": ""}]

def cl(t):
    return re.sub(r'\s+','',re.sub(r'[，。．、；：！？《》（）【】""\'\'…—]','',t)).lower()

def text_match(a, b):
    ca, cb = cl(a), cl(b)
    if ca == cb: return True
    if ca in cb or cb in ca: return True
    if len(ca) > 20 and len(cb) > 20:
        common = sum(1 for ch in ca if ch in cb)
        if common / max(len(ca), len(cb)) > 0.6: return True
    return False

def search_kb(query):
    qc = cl(query)
    best, bs = None, 0
    for x in KB_DATA:
        tc = cl(x['t'])
        s = 0
        if qc == tc: s = 100
        elif tc.find(qc) >= 0 or qc.find(tc) >= 0:
            s = 80 + min(len(qc),len(tc))/max(len(qc),len(tc))*15
        else:
            c = sum(1 for ch in qc if tc.find(ch) >= 0)
            s = 40 + c/max(len(qc),len(tc))*40
        if s > bs and s > 30:
            bs, best = s, x
    return best

PAGE = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
    <title>平海干饭🐎 · 国库知识答题</title>
    <style>
        :root {
            --primary: #4F6EF7; --primary-light: #EEF1FE;
            --success: #22C55E; --warning: #F59E0B; --danger: #EF4444;
            --bg: #F0F4FF; --card: #FFFFFF; --text: #1E293B;
            --text2: #64748B; --border: #E2E8F0;
            --radius: 16px;
        }
        * { margin:0;padding:0;box-sizing:border-box; }
        body {
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
            background: var(--bg); min-height:100vh; padding:24px 16px 40px;
            color:var(--text); -webkit-font-smoothing:antialiased;
        }
        .container { max-width:480px; margin:0 auto; }
        .logo-area { text-align:center; padding:24px 0 20px; }
        .logo-icon {
            width:64px;height:64px; border-radius:18px;
            background:linear-gradient(135deg,#4F6EF7 0%,#7C5CFC 100%);
            display:inline-flex;align-items:center;justify-content:center;
            font-size:32px;color:#fff; margin-bottom:12px;
            box-shadow:0 8px 24px rgba(79,110,247,0.3);
        }
        .logo-title {
            font-size:22px;font-weight:800;
            background:linear-gradient(135deg,#4F6EF7,#7C5CFC);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            letter-spacing:-0.5px;
        }
        .logo-sub { font-size:13px;color:var(--text2);margin-top:2px; }
        .tag-row { display:flex;gap:8px;justify-content:center;margin:0 0 20px;flex-wrap:wrap; }
        .tag { font-size:11px;padding:4px 12px;border-radius:20px;background:var(--primary-light);color:var(--primary);font-weight:600; }
        .tag.green { background:#ECFDF5;color:#059669; }
        .tag.amber { background:#FFFBEB;color:#D97706; }
        .main-card { background:var(--card);border-radius:20px;padding:28px 24px;box-shadow:0 10px 25px rgba(79,110,247,0.12); }
        .input-group { margin-bottom:16px; }
        .input-group textarea {
            width:100%;min-height:56px;max-height:120px;
            border:2px solid var(--border);border-radius:14px;
            padding:14px 16px;font-size:15px;color:var(--text);
            background:#F8FAFC;resize:vertical;outline:none;
            transition:all .25s;font-family:inherit;line-height:1.5;
        }
        .input-group textarea:focus {
            border-color:var(--primary);background:#fff;
            box-shadow:0 0 0 4px rgba(79,110,247,0.1);
        }
        .input-group textarea::placeholder { color:#94A3B8; }
        .btn {
            width:100%;padding:14px;border:none;border-radius:14px;
            font-size:16px;font-weight:700;cursor:pointer;
            transition:all .2s;font-family:inherit;letter-spacing:0.5px;
        }
        .btn:active { transform:scale(0.98); }
        .btn-primary {
            background:linear-gradient(135deg,#4F6EF7,#6366F1);color:#fff;
            box-shadow:0 4px 14px rgba(79,110,247,0.35);margin-bottom:10px;
        }
        .btn-primary:hover { box-shadow:0 6px 20px rgba(79,110,247,0.45); }
        .btn-primary:disabled { background:#CBD5E1;color:#94A3B8;box-shadow:none;cursor:not-allowed; }
        .btn-secondary { background:#F1F5F9;color:var(--text2);font-size:14px;font-weight:600; }
        .btn-secondary:hover { background:#E2E8F0; }
        .status-bar {
            margin-top:16px;padding:12px 16px;border-radius:12px;
            font-size:14px;font-weight:600;display:none;align-items:center;gap:10px;
        }
        .status-bar.show { display:flex; }
        .status-bar.info { background:#EEF2FF;color:#4F6EF7; }
        .status-bar.success { background:#ECFDF5;color:#059669; }
        .status-bar.error { background:#FEF2F2;color:#DC2626; }
        .status-dot { width:8px;height:8px;border-radius:50%;flex-shrink:0; }
        .info .status-dot { background:#4F6EF7;animation:pulse 1.5s infinite; }
        .success .status-dot { background:#22C55E; }
        .error .status-dot { background:#EF4444; }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.8)} }
        .result-section { margin-top:20px; }
        .result-item {
            background:#F8FAFC;border-radius:14px;padding:16px;
            margin-bottom:10px;border:1px solid var(--border);transition:all .2s;
        }
        .result-item.matched { border-color:#BBF7D0;background:#F0FDF4; }
        .result-item .r-header { display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap; }
        .result-item .r-num {
            background:var(--primary);color:#fff;width:24px;height:24px;
            border-radius:8px;display:flex;align-items:center;justify-content:center;
            font-size:12px;font-weight:700;
        }
        .result-item.matched .r-num { background:var(--success); }
        .result-item .r-type { font-size:11px;padding:2px 8px;border-radius:6px;font-weight:600; }
        .type-single { background:#DBEAFE;color:#1D4ED8; }
        .type-multi { background:#FFEDD5;color:#C2410C; }
        .type-judge { background:#F3E8FF;color:#7C3AED; }
        .result-item .r-score { font-size:11px;color:var(--text2);margin-left:auto; }
        .result-item .r-title { font-size:14px;color:var(--text);line-height:1.6;margin-bottom:6px;font-weight:500; }
        .result-item .r-answer { display:inline-flex;align-items:center;gap:6px;font-weight:700;color:var(--success);font-size:15px; }
        .result-item .r-answer .letter {
            width:30px;height:30px;border-radius:10px;background:#DCFCE7;
            color:#15803D;display:flex;align-items:center;justify-content:center;
            font-size:16px;font-weight:800;
        }
        .result-item .r-desc {
            margin-top:8px;padding-top:8px;border-top:1px dashed var(--border);
            font-size:12px;color:var(--text2);line-height:1.7;
        }
        .btn-submit {
            width:100%;padding:16px;border:none;border-radius:14px;
            font-size:17px;font-weight:700;font-family:inherit;
            background:linear-gradient(135deg,#22C55E,#16A34A);color:#fff;
            cursor:pointer;margin-top:8px;letter-spacing:0.5px;
            box-shadow:0 4px 14px rgba(34,197,94,0.35);
        }
        .btn-submit:active { transform:scale(0.98); }
        .footer { text-align:center;padding:24px 0 16px;font-size:12px;color:#94A3B8; }
        .footer .brand { font-weight:700;background:linear-gradient(135deg,#4F6EF7,#7C5CFC);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }
        .saved-bar { display:none;background:#ECFDF5;border:1px solid #BBF7D0;border-radius:12px;padding:10px 14px;margin-bottom:16px;font-size:13px;color:#059669;text-align:center;font-weight:600; }
        .guide {
            margin-top:14px;padding:14px;background:#F8FAFC;
            border-radius:12px;font-size:12px;color:var(--text2);line-height:1.8;
        }
        .guide b { color:var(--primary); }
    </style>
</head>
<body>
<div class="container">
    <div class="logo-area">
        <div class="logo-icon">🐎</div>
        <div class="logo-title">平海干饭🐎</div>
        <div class="logo-sub">国库知识 · 智能答题助手</div>
    </div>
    <div class="tag-row">
        <span class="tag">📚 60题题库</span>
        <span class="tag green">🎯 精准匹配</span>
        <span class="tag amber">⚡ 一键提交</span>
    </div>
    <div class="main-card" id="mainCard">
        <div class="saved-bar" id="savedBar">✅ 已记住账号，直接点开始即可</div>
        <div class="input-group" id="inputGroup">
            <textarea id="urlInput" placeholder="在此粘贴完整答题链接&#10;或输入32位 uuid ..." autocomplete="off"></textarea>
        </div>
        <button class="btn btn-primary" id="btnStart" onclick="startAuto()">🚀 开始自动答题</button>
        <button class="btn btn-secondary" onclick="pasteFromClipboard()">📋 从剪贴板粘贴</button>
        <button class="btn btn-secondary" id="clearBtn" onclick="clearSaved()" style="display:none">🔓 切换账号</button>
        <div class="status-bar" id="status"><span class="status-dot"></span><span id="statusText"></span></div>
        <div class="result-section" id="resultArea"></div>
        <div class="guide">
            📌 <b>操作提示：</b><br>
            ① 手机微信答题页 → 转发到<b>文件传输助手</b><br>
            ② 电脑微信打开链接 → 复制网址<br>
            ③ 粘贴到上方输入框 → 点开始<br>
            <span style="color:#94A3B8;">支持粘贴完整链接或仅 uuid</span>
        </div>
    </div>
    <div class="footer">Powered by <span class="brand">图图J</span> · 仅供学习参考</div>
</div>
<script>
var currentKey='',currentUuid='',cachedAnswers=null;
var btnStart=document.getElementById('btnStart');
var statusEl=document.getElementById('status');
var statusText=document.getElementById('statusText');
var resultArea=document.getElementById('resultArea');
function showStatus(msg,type){
    statusEl.className='status-bar show '+(type||'info');
    statusEl.style.display='flex';statusText.textContent=msg;
}
function apiCall(endpoint,method,body){
    return fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({endpoint:endpoint,method:method||'GET',body:body||null})
    }).then(function(r){return r.json()});
}
var savedBar=document.getElementById('savedBar');
var inputGroup=document.getElementById('inputGroup');
var clearBtn=document.getElementById('clearBtn');
var urlInput=document.getElementById('urlInput');

// 初始化：尝试从localStorage恢复uuid
(function(){
    try{var suid=localStorage.getItem('gk_uid');if(suid){currentUuid=suid;currentKey='eeeddc4f487b4bf7b0c9f1dad5d1ff99';showSaved()}}catch(e){}
})();

function showSaved(){
    currentKey='eeeddc4f487b4bf7b0c9f1dad5d1ff99';
    savedBar.style.display='block';inputGroup.style.display='none';clearBtn.style.display='block';
}
function hideSaved(){
    currentKey='';currentUuid='';
    savedBar.style.display='none';inputGroup.style.display='block';clearBtn.style.display='none';
}
function saveUid(){
    try{localStorage.setItem('gk_uid',currentUuid)}catch(e){}
    currentKey='eeeddc4f487b4bf7b0c9f1dad5d1ff99';
    savedBar.style.display='block';inputGroup.style.display='none';clearBtn.style.display='block';
}
function clearSaved(){
    try{localStorage.removeItem('gk_uid')}catch(e){}
    currentUuid='';currentKey='';urlInput.value='';hideSaved();showStatus('已清除，可输入新账号','info');
    setTimeout(function(){urlInput.focus()},200);
}

function startAuto(){
    var input=document.getElementById('urlInput').value.trim();
    if(!input && currentUuid){doAutoAnswer();return;}
    if(!input){showStatus('请粘贴答题链接或输入uuid','error');return;}
    showStatus('🔍 正在解析输入...','info');
    var km=input.match(/key=([^&]+)/),um=input.match(/uuid=([^&]+)/);
    if(km&&um){currentKey=km[1];currentUuid=um[1];}
    else{var uo=input.match(/[a-f0-9]{32}/i);
        if(uo){currentKey='eeeddc4f487b4bf7b0c9f1dad5d1ff99';currentUuid=uo[0];}
        else{showStatus('未识别到uuid，请确认输入正确','error');return;}
    }
    saveUid();
    doAutoAnswer();
}
function doAutoAnswer(){
    resultArea.innerHTML='';btnStart.disabled=true;btnStart.textContent='⏳ 自动答题中...';
    showStatus('① 正在检查账号状态...','info');
    apiCall('/checkInfo?uuid='+currentUuid+'&key='+currentKey,'GET')
    .then(function(d){
        if(d.code==='2300'){showStatus('② 已注册，获取题目中...','info');return{code:'200'};}
        else if(d.code==='2200'){showStatus('② 需要注册，请填写信息...','info');
            // 弹出注册表单
            return new Promise(function(resolve,reject){
                showRegForm(resolve,reject);
            });
        }else if(d.code==='1000')throw new Error('今日答题次数已用完');
        else throw new Error(d.message||'状态异常('+d.code+')');
    }).then(function(r){
        if(r.code&&r.code!=='200')throw new Error(r.message||'注册失败');
        showStatus('③ 正在获取题目...','info');
        return apiCall('/exam/getExam','POST',{key:currentKey,uuid:currentUuid});
    }).then(function(e){
        if(e.code!=='200')throw new Error(e.message||'获取题目失败');
        showStatus('④ 正在匹配答案...','info');
        return fetch('/api/matchAnswers',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({examData:e.data||[],key:currentKey,uuid:currentUuid})
        }).then(function(r){return r.json()});
    }).then(function(m){
        if(m.error)throw new Error(m.error);
        var details=m.details||[];cachedAnswers=m.answers||[];
        showStatus('✅ 匹配完成！共 '+details.length+' 题','success');
        var tc={1:'type-single',2:'type-multi',3:'type-judge'},tn={1:'单选',2:'多选',3:'判断'};
        var html='';
        details.forEach(function(d){
            var cls=d.matched?'matched':'',sc=d.score>=80?'#059669':d.score>0?'#D97706':'#DC2626';
            html+='<div class="result-item '+cls+'">';
            html+='<div class="r-header">';
            html+='<span class="r-num">'+d.index+'</span>';
            html+='<span class="r-type '+(tc[d._type]||'type-single')+'">'+d.type+'</span>';
            html+='<span class="r-score" style="color:'+sc+'">匹配 '+d.score+'%</span></div>';
            html+='<div class="r-title">'+escapeHtml(d.title)+'</div>';
            html+='<div class="r-answer"><span class="letter">'+escapeHtml(d.answer)+'</span> 正确答案</div>';
            if(d.desc)html+='<div class="r-desc">📖 '+escapeHtml(d.desc.substring(0,150))+'</div>';
            html+='</div>';
        });
        if(m.all_matched)html+='<button class="btn-submit" onclick="doSubmit()">📤 提交答案 · 查看成绩</button>';
        else html+='<p style="color:#DC2626;text-align:center;padding:12px;">⚠️ 部分题目未匹配</p>';
        resultArea.innerHTML=html;btnStart.disabled=false;btnStart.textContent='🔄 重新答题';
    }).catch(function(err){
        showStatus('❌ '+err.message,'error');
        btnStart.disabled=false;btnStart.textContent='🚀 开始自动答题';
    });
}
var PROV_DATA = null;
fetch("https://file.njsummer.cn/gkzsactivity/js/province-city.json").then(function(r){return r.json()}).then(function(d){PROV_DATA=d});

function showRegForm(resolve,reject){
    window._regResolve = resolve;
    window._regReject = reject;
    showStatus('📝 请填写注册信息','info');
    
    var h = '<div style="text-align:left;padding:4px 0;">';
    // 昵称
    h += '<div style="margin-bottom:14px;"><label style="font-size:13px;color:var(--t2);display:block;margin-bottom:4px;">昵称 <span style="color:#EF4444">*</span></label><input id="regNick" style="width:100%;padding:10px 12px;border:2px solid var(--b);border-radius:10px;font-size:14px;outline:none;background:#F8FAFC;color:var(--t);" placeholder="请输入姓名或昵称"></div>';
    // 省份选择
    h += '<div style="margin-bottom:6px;"><label style="font-size:13px;color:var(--t2);display:block;margin-bottom:4px;">省份/单列市 <span style="color:#EF4444">*</span></label>';
    h += '<select id="regProv" onchange="onProvChange()" style="width:100%;padding:10px 12px;border:2px solid var(--b);border-radius:10px;font-size:14px;outline:none;background:#F8FAFC;color:var(--t);appearance:auto;"><option value="">请选择省份</option>';
    if(PROV_DATA){PROV_DATA.forEach(function(p){h+='<option value="'+p.province+'">'+p.province+'</option>'})}
    h += '</select></div>';
    // 城市选择
    h += '<div style="margin-bottom:14px;"><select id="regCity" style="width:100%;padding:10px 12px;border:2px solid var(--b);border-radius:10px;font-size:14px;outline:none;background:#F8FAFC;color:var(--t);appearance:auto;"><option value="">请先选择省份</option></select></div>';
    // 单位
    h += '<div style="margin-bottom:14px;"><label style="font-size:13px;color:var(--t2);display:block;margin-bottom:4px;">单位名称</label><input id="regCompany" style="width:100%;padding:10px 12px;border:2px solid var(--b);border-radius:10px;font-size:14px;outline:none;background:#F8FAFC;color:var(--t);" placeholder="选填"></div>';
    // 按钮
    h += '<button class="btn btn-p" onclick="submitRegForm()">✅ 提交并继续</button>';
    h += '<button class="btn btn-s" onclick="cancelRegForm()">取消</button>';
    h += '</div>';
    resultArea.innerHTML = h;
}

function onProvChange(){
    var pv = document.getElementById('regProv').value;
    var citySel = document.getElementById('regCity');
    citySel.innerHTML = '<option value="">请选择城市</option>';
    if(!pv||!PROV_DATA)return;
    for(var i=0;i<PROV_DATA.length;i++){
        if(PROV_DATA[i].province===pv){
            PROV_DATA[i].cities.forEach(function(c){citySel.innerHTML+='<option value="'+c+'">'+c+'</option>'});
            break;
        }
    }
}

function submitRegForm(){
    var nick = (document.getElementById('regNick')||{}).value||'';
    var prov = (document.getElementById('regProv')||{}).value||'';
    var city = (document.getElementById('regCity')||{}).value||'';
    var company = (document.getElementById('regCompany')||{}).value||'';
    if(!nick.trim()){showStatus('请填写昵称','error');return;}
    if(!prov){showStatus('请选择省份','error');return;}
    if(!city){showStatus('请选择城市','error');return;}
    showStatus('② 正在提交注册信息...','info');
    apiCall('/updateInfo','POST',{key:currentKey,uuid:currentUuid,province:prov,city:city,nickName:nick.trim(),company:company.trim(),phone:''})
    .then(function(r){
        if(r.code&&r.code!=='200')throw new Error(r.message||'注册失败');
        window._regResolve(r);
    }).catch(function(e){
        showStatus('注册失败: '+e.message,'error');
        if(window._regReject)window._regReject(e);
    });
}

function cancelRegForm(){
    showStatus('已取消','info');
    btnStart.disabled=false;btnStart.textContent='🚀 开始自动答题';
    if(window._regReject)window._regReject(new Error('用户取消'));
}

var _submitting=false;

function doSubmit(){
    if(_submitting){showStatus('正在提交中，请勿重复点击','error');return;}
    if(!cachedAnswers||cachedAnswers.length===0){showStatus('没有可提交的答案','error');return;}
    _submitting=true;
    // 禁用提交按钮
    var sb = document.querySelector('.btn-submit');
    if(sb){sb.disabled=true;sb.textContent='⏳ 提交中...';sb.style.opacity='0.6';}
    btnStart.disabled=true;showStatus('📤 正在提交答案...','info');
    apiCall('/exam/submit','POST',{time:30,dtoList:cachedAnswers,aid:currentKey,uuid:currentUuid})
    .then(function(d){
        if(d.code==='200'||d.code==='800'){
            var score=(d.data&&d.data.score!=null)?d.data.score:(typeof d.data==='number'?d.data:(d.data||'100'));
            showStatus('🎉 得分: '+score+' 分！正在跳转结果页...','success');
            setTimeout(function(){
                window.location.href='http://file.njsummer.cn/gkzsactivity/success.html?key='+currentKey+'&score='+score+(d.code==='800'?'&result=800':'');
            },1000);
        }else if(d.code==='1000'){showStatus('今日答题次数已用完','error');}
        else{showStatus('提交失败: ['+d.code+'] '+(d.message||''),'error');}
        _submitting=false;
        btnStart.disabled=false;btnStart.textContent='🚀 开始自动答题';
        if(sb){sb.disabled=false;sb.textContent='📤 提交答案 · 查看成绩';sb.style.opacity='1';}
    }).catch(function(err){
        showStatus('提交失败: '+err.message,'error');
        _submitting=false;
        btnStart.disabled=false;btnStart.textContent='🚀 开始自动答题';
        if(sb){sb.disabled=false;sb.textContent='📤 提交答案 · 查看成绩';sb.style.opacity='1';}
    });
}
function pasteFromClipboard(){
    if(!navigator.clipboard){showStatus('请手动 Ctrl+V 粘贴','error');return;}
    navigator.clipboard.readText().then(function(t){
        document.getElementById('urlInput').value=t;
        showStatus('已粘贴 ✅ 点击上方按钮开始','success');
    }).catch(function(){showStatus('请手动 Ctrl+V 粘贴到输入框','error');});
}
function escapeHtml(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML;}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return PAGE

@app.route("/api", methods=["POST"])
def api_proxy():
    d = request.get_json()
    endpoint = d.get("endpoint", "")
    method = d.get("method", "GET").upper()
    body = d.get("body")
    url = API_BASE + endpoint
    headers = {"Content-Type": "application/json", "Accept": "application/json",
               "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"}
    if "/exam/submit" in endpoint and body:
        body.pop("token", None)
    try:
        if method == "GET":
            resp = req.get(url, params=body or {}, headers=headers, timeout=15)
        else:
            resp = req.post(url, json=body, headers=headers, timeout=15)
        return jsonify(resp.json())
    except req.exceptions.Timeout:
        return jsonify({"code": "error", "message": "请求超时"})
    except Exception as e:
        return jsonify({"code": "error", "message": str(e)})

@app.route("/match", methods=["POST"])
def match_answers():
    d = request.get_json()
    questions = d.get("examData", [])
    if isinstance(questions, dict):
        questions = [v for v in questions.values() if isinstance(v, dict) and "idStr" in v]
    answers, details = [], []
    tn = {1: "单选", 2: "多选", 3: "判断"}
    for i, q in enumerate(questions):
        title = q.get("title", "")
        qtype = q.get("type", 1)
        api_opts = q.get("options", [])
        m = search_kb(title)
        detail = {"index": i+1, "type": tn.get(qtype, "?"), "title": title[:80], "_type": qtype}
        if m:
            detail.update({"matched": True, "score": round(m["s"]), "desc": m["d"]})
            correct_texts = m.get("ct", "").split("|")
            if qtype == 2:  # 多选
                indices = []
                for ct in correct_texts:
                    ct = ct.strip()
                    if not ct: continue
                    for opt in api_opts:
                        if text_match(ct, opt.get("option", "")):
                            indices.append(opt.get("index", ""))
                            break
                ans_val = ",".join(indices) if indices else m["a"]
            elif qtype == 3:  # 判断
                ans_val = ""
                for opt in api_opts:
                    if text_match(correct_texts[0], opt.get("option", "")):
                        ans_val = opt.get("index", "")
                        break
                if not ans_val: ans_val = m["a"]
            else:  # 单选
                ans_val = ""
                for opt in api_opts:
                    if text_match(correct_texts[0], opt.get("option", "")):
                        ans_val = opt.get("index", "")
                        break
                if not ans_val: ans_val = m["a"]
            detail["answer"] = ans_val
            answers.append({"idStr": q.get("idStr", ""), "answer": ans_val})
        else:
            detail.update({"matched": False, "score": 0, "answer": "?", "desc": "未匹配"})
        details.append(detail)
    result = {"details": details, "answers": answers, "all_matched": len(answers) == len(questions)}
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
