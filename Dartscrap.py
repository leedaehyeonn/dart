#dart 크롤링 개발에서 가장 중요한 부분. 단위시간당 url호출을 제한횟수보다 많이 하면 ip가 차단당한다. 회사에서 ip가 차단되면 증권사는 발행을 못할지도..
#반드시 외부 망 개인ip로 접근하든, 검증된 코드를 쓰자.
"""URL = 'https://opendart.fss.or.kr/api/list.xml'
crtfc_key =	''
corp_code =	 ""#거래소용 ticker가 아니라 금감원용 코드가 따로 있음
bgn_de	= ""#시작일(YYYYMMDD)
end_de = ""#종료일
last_reprt_at = ""
pblntf_ty = ""#공시유형 
# A : 정기공시
# B : 주요사항보고
# C : 발행공시
# D : 지분공시
# E : 기타공시
# F : 외부감사관련
# G : 펀드공시
# H : 자산유동화
# I : 거래소공시
# J : 공정위공시
page_no	= 1	
page_count = 100"""


import pandas as pd
from bs4 import BeautifulSoup #html 웹문서를 파싱, 조회하는 모듈
import requests #url을 호출하는 모듈. url+요청인자에서 요청인자를 딕셔너리로 받음
from datetime import datetime as dt



#corp_code 따오기
def get_DART_corpcode():
    import pandas as pd
    from xml.etree.ElementTree import parse
    xmlTree = parse(r'C:\PythonProject\student\Dart api\CORPCODE.xml')
    root = xmlTree.getroot()
    temp_list = root.findall('list')

    list_for_df = []
    for i in range(0,len(temp_list)):
        list_for_df.append(
        [temp_list[i].findtext('corp_code'),
        temp_list[i].findtext('corp_name'),
        temp_list[i].findtext('stock_code'),
        temp_list[i].findtext('modify_date')]
        )
    corp_code_df = pd.DataFrame(list_for_df, columns = ['corp_code','corp_name','stock_code','modify_date'])
    # corp_code_df.to_excel('CorpCode.xlsx')
    return corp_code_df


def get_search_html(bgn_de, end_de, page_no=1 , page_count=100, pblntf_ty = 'B'):
    """전체 기업 주요사항보고(B) 가져오기"""
    key = crtfc_key
    url = 'https://opendart.fss.or.kr/api/list.xml'
    params = { 
        'crtfc_key' : key,
        'bgn_de' : bgn_de,
        'end_de' : end_de,
        'page_no' : page_no,
        'page_count' : page_count,
        'pblntf_ty' : pblntf_ty
    }
    response = requests.get(url,params=params).content.decode('UTF-8')
    html = BeautifulSoup(response, 'xml') #html로 변환
    res = html.findAll('list')
    return res

def Report(bgn_de, end_de, page_no, page_count, pblntf_ty = 'B'):
    """주요사항보고 가져온 후, html 파싱"""
    result = get_search_html(bgn_de, end_de, page_no, page_count, pblntf_ty = 'B')
    list_for_df = []
    for i in result:
        list_for_df.append([
            i.corp_code.text,
            i.flr_nm.text,
            i.report_nm.text,
            'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+i.rcept_no.text]) #rcept 넘버가 공시접수번호이기 때문에 알면 바로접속가능

    report_df = pd.DataFrame(list_for_df,columns=['회사코드','회사명','공시내용','공시링크'])
    return report_df

def target_corp_html(corp_code, bgn_de, end_de, page_no, page_count, pblntf_ty = 'B'):
    """특정기업 주요사항보고(B) 가져오기"""
    key = crtfc_key
    url = 'https://opendart.fss.or.kr/api/list.xml'
    params = { 
        'crtfc_key' : key,
        'corp_code' : corp_code,
        'bgn_de' : bgn_de,
        'end_de' : end_de,
        'page_no' : page_no,
        'page_count' : page_count,
        'pblntf_ty' : pblntf_ty
    }
    response = requests.get(url,params=params).content.decode('UTF-8')
    html = BeautifulSoup(response, 'xml') #html로 변환
    res = html.findAll('list')
    return res

def target_corp_Report(corp_code, bgn_de, end_de, page_no, page_count, pblntf_ty):
    """get_search_B 주요사항보고 가져온 후, html 파싱"""
    result = target_corp_html(corp_code, bgn_de, end_de, page_no, page_count, pblntf_ty)
    list_for_df = []
    for i in result:
        list_for_df.append([
            i.corp_code.text,
            i.flr_nm.text,
            i.report_nm.text,
            'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+i.rcept_no.text]) #rcept 넘버가 공시접수번호이기 때문에 알면 바로접속가능

    report_df = pd.DataFrame(list_for_df,columns=['회사코드','회사명','공시내용','공시링크'])
    return report_df

#유상증자 공시내용 가져오기 (개발가이드 이용)
def get_pifricDecsn_details(corp_code, bgn_de, end_de):
    key = crtfc_key
    url = 'https://opendart.fss.or.kr/api/piicDecsn.xml'
    params = {
        'crtfc_key' : key,
        'corp_code' : corp_code,
        'bgn_de' : bgn_de,
        'end_de' : end_de
    }
    response = requests.get(url, params=params).content.decode('UTF-8')
    html = BeautifulSoup(response,'html.parser')
    res_dict = {
        "회사명" : html.corp_name.text\
        ,'신주수(보통)' : html.nstk_ostk_cnt.text\
        ,'신주수(기타)' : html.nstk_estk_cnt.text\
        ,'주당액면가' : html.fv_ps.text\
        ,'증자전 발행주식총수(보통주)' : html.bfic_tisstk_ostk.text\
        ,'증자전 발행주식총수(기타주)' : html.bfic_tisstk_estk.text\
        ,'증자방식' : html.ic_mthn.text
    }
    return res_dict

def 정기분기보고서(target_list, bgn_de, end_de):
    df = get_DART_corpcode()
    target_df = {}
    for target in target_list:
        corp_code = df.loc[df['corp_name'] == target, 'corp_code'].values[0]
        result = target_corp_Report(corp_code, bgn_de, end_de, page_no=1, page_count=100, pblntf_ty='A')
        target_df[target] = result

    df_target = pd.concat(target_df.values(), keys=target_df.keys(), axis=0)
    return df_target

crtfc_key =	''
# corp_code =	 "" 거래소용 ticker가 아니라 금감원용 코드가 따로 있음
bgn_de	= "20230101"#시작일(YYYYMMDD)
end_de = "20240115"
pblntf_ty = 'B'
page_no	= 1	
page_count = 100

# get_search_html(bgn_de, end_de, page_no=1, page_count=10, pblntf_ty='B')
Report(end_de, end_de,page_no=1, page_count=100, pblntf_ty='B')

target_corp_Report('00126380', bgn_de, end_de, page_no=1, page_count=100, pblntf_ty='A')
target_corp_html('00126380', bgn_de, end_de,page_no=1, page_count=100, pblntf_ty='A')


####분기/반기/ 다 가져오기..####
# df = get_DART_corpcode()
# target_list = ['삼성전자', 'HMM']
# target_df = {}
# for target in target_list:
#     corp_code = df.loc[df['corp_name'] == target, 'corp_code'].values[0]
#     result = target_corp_Report(corp_code, bgn_de, end_de, page_no=1, page_count=100, pblntf_ty='A')
#     target_df[target] = result

# df_target = pd.concat(target_df.values(), keys=target_df.keys(), axis=0)



target_list = ['삼성전자', 'HMM']



정기분기보고서(target_list,bgn_de,end_de)  