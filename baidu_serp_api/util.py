from datetime import datetime, timedelta
import random
import string
import re
from bs4 import BeautifulSoup
from loguru import logger
import uuid
import random, hashlib
import time

# 生成PC端浏览器风格的Cookie
def gen_pc_cookies(random_params=None):
    """
    基于真实浏览器Cookie结构生成逼真的Cookie
    某些cookie值与URL参数保持一致以模拟真实浏览器行为
    """
    # 生成32位十六进制BAIDUID
    baiduid = uuid.uuid4().hex.upper()[:32]
    
    # BIDUPSID使用相似但不同的32位十六进制  
    bidupsid = uuid.uuid4().hex.upper()[:32]
    
    # 当前时间戳
    pstm = int(time.time())
    
    # 生成较小的随机数作为BDSVRTM
    bdsvrtm = random.randint(10, 999)
    
    # 生成32位混合字符串作为BA_HECTOR
    ba_hector = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    
    # 生成32位十六进制大写作为BDORZ
    bdorz = uuid.uuid4().hex.upper().replace('-', '')
    
    # 生成6位随机数字作为BD_UPN
    bd_upn = random.randint(100000, 999999)
    
    # 生成H_PS_PSSID - 多个数字用下划线连接
    h_ps_pssid_numbers = [random.randint(60000, 65000) for _ in range(20)]
    h_ps_pssid = '_'.join(map(str, h_ps_pssid_numbers))
    
    # 生成H_PS_645EC - 随机字符串，如果有random_params则使用其中的rsv_t
    if random_params and 'rsv_t' in random_params:
        h_ps_645ec = random_params['rsv_t'][:43]  # 使用rsv_t的前43位
    else:
        h_ps_645ec = ''.join(random.choices(string.ascii_letters + string.digits, k=43))
    
    # 生成ZFY - Base64风格字符串
    zfy = ''.join(random.choices(string.ascii_letters + string.digits + '+/:', k=43))
    
    # 生成标准UUID格式的baikeVisitId
    baike_visit_id = str(uuid.uuid4())
    
    # 生成复杂的COOKIE_SESSION
    session_parts = [random.randint(0, 20) for _ in range(18)]
    session_timestamp = int(time.time())
    cookie_session = '_'.join(map(str, session_parts)) + f'%7C5%230_0_{session_timestamp}%7C1'
    
    # 组装Cookie字符串
    cookies = [
        f"BIDUPSID={bidupsid}",
        f"PSTM={pstm}",
        f"BAIDUID={baiduid}:FG=1",
        "delPer=0",
        "BD_CK_SAM=1",
        "PSINO=5",
        f"BD_UPN={bd_upn}",
        f"BAIDUID_BFESS={baiduid}:FG=1",
        f"BDORZ={bdorz}",
        f"BA_HECTOR={ba_hector}",
        f"H_WISE_SIDS={h_ps_pssid}",
        f"ZFY={zfy}",
        f"H_PS_PSSID={h_ps_pssid}",
        f"H_PS_645EC={h_ps_645ec}",
        f"baikeVisitId={baike_visit_id}",
        f"BDSVRTM={bdsvrtm}",
        f"COOKIE_SESSION={cookie_session}"
    ]
    
    return '; '.join(cookies)

# 生成移动端浏览器风格的Cookie
def gen_mobile_cookies(random_params=None):
    """
    基于真实移动端浏览器Cookie结构生成逼真的Cookie
    某些cookie值与URL参数保持一致以模拟真实浏览器行为
    """
    # 生成基础ID，如果有random_params则使用其中的baiduid
    if random_params and 'baiduid' in random_params:
        baiduid = random_params['baiduid']
    else:
        baiduid = uuid.uuid4().hex.upper()[:32]
    
    # 生成rsv_i - 复杂编码字符串
    rsv_i = ''.join(random.choices(string.ascii_letters + string.digits + '+/=', k=64))
    
    # 生成BA_HECTOR - 32位混合字符串
    ba_hector = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    
    # 生成BDORZ - 32位十六进制大写
    bdorz = uuid.uuid4().hex.upper().replace('-', '')
    
    # 生成ZFY - Base64风格字符串
    zfy = ''.join(random.choices(string.ascii_letters + string.digits + '+/:', k=43))
    
    # 生成H_WISE_SIDS - 移动端特有的长串数字ID
    h_wise_sids_numbers = [random.randint(110000, 670000) for _ in range(80)]
    h_wise_sids = '_'.join(map(str, h_wise_sids_numbers))
    
    # 生成时间戳相关
    current_timestamp = int(time.time())
    bdsvrtm = random.randint(1, 10)
    
    # 生成__bsi - 特殊格式会话ID
    bsi_id = ''.join(random.choices(string.digits, k=19))
    bsi = f"{bsi_id}_00_{random.randint(1, 10)}_R_N_{random.randint(1, 50)}_{random.randint(1000, 9999)}_c02f_Y"
    
    # 生成COOKIE_SESSION - 复杂会话信息
    session_parts = [random.randint(0, 10) for _ in range(15)]
    cookie_session = '_'.join(map(str, session_parts)) + f'_{current_timestamp}%7C2%230_0_0_0_0_0_0_0_{current_timestamp}%7C1'
    
    # 生成FC_MODEL - 功能模型参数
    fc_model_parts = ['0'] * 15
    fc_model_parts[4] = f"{random.uniform(200, 300):.2f}"
    fc_model_parts[10] = f"{random.uniform(200, 300):.2f}"
    fc_model = '_'.join(fc_model_parts) + f'_{current_timestamp}%7C2%23{fc_model_parts[4]}_0_0_0_0_0_{current_timestamp}%7C2%230_apx_0_0_0_0_0_{current_timestamp}'
    
    # 生成其他随机值
    msa_wh = f"{random.randint(1200, 1600)}_{random.randint(700, 900)}"
    msa_pbt = random.randint(100, 200)
    msa_zoom = random.randint(900, 1100)
    msa_phy_wh = f"{random.randint(1600, 2000)}_{random.randint(2500, 3000)}"
    
    # 组装Cookie字符串
    cookies = [
        f"rsv_i={rsv_i}",
        f"BA_HECTOR={ba_hector}",
        f"BDORZ={bdorz}",
        f"ZFY={zfy}",
        f"H_WISE_SIDS={h_wise_sids}",
        "delPer=0",
        f"BDSVRTM={bdsvrtm}",
        f"H_WISE_SIDS_BFESS={h_wise_sids}",
        f"BAIDUID={baiduid}:FG=1",
        f"BAIDUID_BFESS={baiduid}:FG=1",
        "POLYFILL=0",
        f"MSA_WH={msa_wh}",
        f"MSA_PBT={msa_pbt}",
        f"MSA_ZOOM={msa_zoom}",
        "wpr=0",
        f"MSA_PHY_WH={msa_phy_wh}",
        f"__bsi={bsi}",
        f"COOKIE_SESSION={cookie_session}",
        f"FC_MODEL={fc_model}"
    ]
    
    return '; '.join(cookies)

# 生成随机参数
def gen_random_params():
    """
    生成搜索所需的随机参数
    只保留PC版和Mobile版仍在使用的参数
    """
    # PC版使用的参数
    rsv_pq = hex(random.getrandbits(64))
    rsv_t = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()
    
    # Mobile版Cookie和基础功能使用的参数
    bduss = ''.join(random.choices(string.ascii_letters + string.digits, k=176))
    baiduid = uuid.uuid4().hex.upper()[:32]
    timestamp = int(time.time() * 1000)
    r = ''.join(random.choices(string.digits, k=4))

    # Mobile版URL请求参数中特有的参数（PC版不使用）
    rsv_iqid = ''.join(random.choices(string.digits, k=19))
    rqid = rsv_iqid  # 通常与rsv_iqid相同
    sugid = ''.join(random.choices(string.digits, k=14))
    rsv_sug4_timestamp = int(time.time() * 1000)
    input_timestamp = rsv_sug4_timestamp + random.randint(1000, 3000)

    return {
        'rsv_pq': rsv_pq,
        'rsv_t': rsv_t,
        'bduss': bduss,
        'baiduid': baiduid,
        'timestamp': timestamp,
        'r': r,
        # Mobile版URL请求参数中特有的参数
        'rsv_iqid': rsv_iqid,
        'rqid': rqid,
        'sugid': sugid,
        'rsv_sug4': rsv_sug4_timestamp,
        'inputT': input_timestamp
    }

# 清理html标签
def clean_html_tags(html_content):
    clean_text = re.sub('<[^<]+?>|\\n', '', html_content)
    clean_text = ' '.join(clean_text.split())
    return clean_text

def convert_date_format(date_str):
    date_formats = [
        (r"(\d+)分钟前", lambda m: (datetime.now() - timedelta(minutes=int(m.group(1)))).strftime('%Y-%m-%d')),
        (r"(\d+)小时前", lambda m: (datetime.now() - timedelta(hours=int(m.group(1)))).strftime('%Y-%m-%d')),
        (r"今天", lambda m: datetime.now().strftime('%Y-%m-%d')),
        (r"昨天", lambda m: (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')),
        (r"昨天 (\d+:\d+)", lambda m: (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')),
        (r"前天", lambda m: (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')),
        (r"前天 (\d+:\d+)", lambda m: (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')),
        (r"(\d+)天前", lambda m: (datetime.now() - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d')),
        (r"(\d+)月(\d+)日", lambda m: f"{datetime.now().strftime('%Y')}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"),
        (r"(\d+)年(\d+)月(\d+)日", lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}")
    ]
    
    for fmt, func in date_formats:
        match = re.match(fmt, date_str)
        if match:
            return func(match)
    return date_str