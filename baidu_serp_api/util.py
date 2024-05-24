import random
import string
import re
from bs4 import BeautifulSoup
from loguru import logger
import uuid
import random, hashlib
import time

# 生成随机参数
def gen_random_params():
    bduss = ''.join(random.choices(string.ascii_letters + string.digits, k=176))
    baiduid = uuid.uuid4().hex.upper()[:32]
    isid = uuid.uuid4().hex
    rsv_pq = hex(random.getrandbits(64))
    rsv_t = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()
    rsv_sid = '_'.join([str(random.randint(60000, 60300)) for _ in range(6)])
    clist = uuid.uuid4().hex
    _cr1 = hashlib.md5(str(random.getrandbits(128)).encode('utf-8')).hexdigest()
    timestamp = int(time.time() * 1000)
    r = ''.join(random.choices(string.digits, k=4))

    return {
        'bduss': bduss,
        'baiduid': baiduid,
        'isid': isid,
        'rsv_pq': rsv_pq,
        'rsv_t': rsv_t,
        'rsv_sid': rsv_sid,
        'clist': clist,
        '_cr1': _cr1,
        'timestamp': timestamp,
        'r': r
    }

# 清理html标签
def clean_html_tags(html_content):
    clean_text = re.sub('<[^<]+?>|\\n', '', html_content)
    clean_text = ' '.join(clean_text.split())
    return clean_text