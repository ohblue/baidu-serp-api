import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .baidu_pc import BaiduPc
from .baidu_mobile import BaiduMobile

__all__ = ['BaiduPc', 'BaiduMobile']
