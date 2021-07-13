# -*- coding: utf8 -*-
import re
import json
import time
import requests
from bs4 import BeautifulSoup

# 强烈建议部署在非大陆区域，例如HK、SG等

USERNAME = '' # 这里填用户名，邮箱也可
PASSWORD = ''  # 这里填密码

# Server酱 http://sc.ftqq.com/?c=code
SCKEY = '' # 这里填Server酱的key，无需推送可不填 示例: SCU646xxxxxxxxdacd6a5dc3f6

# 酷推 https://cp.xuthus.cc
CoolPush_Skey = ''
# 通知类型 CoolPush_MODE的可选项有（默认send）：send[QQ私聊]、group[QQ群聊]、wx[个微]、ww[企微]
CoolPush_MODE = 'send'

# PushPlus https://pushplus.hxtrip.com/message
PushPlus_Token = ''

desp = '' # 不用动

def print_(info):
    print(info)
    global desp
    desp = desp + info + '\n\n'


def login(username, password) -> (str, requests.session):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36",
        "origin": "https://www.euserv.com",
        "host": "support.euserv.com"
    }
    url = "https://support.euserv.com/index.iphp"
    session = requests.Session()

    sess = session.get(url, headers=headers)
    sess_id = re.findall("PHPSESSID=(\\w{10,100});", str(sess.headers))[0]
    # 访问png
    png_url = "https://support.euserv.com/pic/logo_small.png"
    session.get(png_url, headers=headers)
    login_data = {
        "email": username,
        "password": password,
        "form_selected_language": "en",
        "Submit": "Login",
        "subaction": "login",
        "sess_id": sess_id
    }
    url = "https://support.euserv.com/index.iphp"
    session = requests.Session()
    f = session.post(url, headers=headers, data=login_data, verify=False)
    f.raise_for_status()
    if f.text.find('Hello') == -1:
        return '-1', session
    return sess_id, session


def get_servers(sess_id, session) -> {}:
    d = {}
    url = "https://support.euserv.com/index.iphp?sess_id=" + sess_id
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36",
        "origin": "https://www.euserv.com",
        "host": "support.euserv.com"
    }
    f = session.get(url=url, headers=headers, verify=False)
    f.raise_for_status()
    soup = BeautifulSoup(f.text, 'html.parser')
    for tr in soup.select('#kc2_order_customer_orders_tab_content_1 .kc2_order_table.kc2_content_table tr'):
        server_id = tr.select('.td-z1-sp1-kc')
        if not len(server_id) == 1:
            continue
        flag = True if tr.select('.td-z1-sp2-kc .kc2_order_action_container')[
                           0].get_text().find('Contract extension possible from') == -1 else False
        d[server_id[0].get_text()] = flag
    return d


def renew(sess_id, session, password, order_id) -> bool:
    url = "https://support.euserv.com/index.iphp"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36",
        "Host": "support.euserv.com",
        "origin": "https://support.euserv.com",
        "Referer": "https://support.euserv.com/index.iphp"
    }
    data = {
        "Submit": "Extend contract",
        "sess_id": sess_id,
        "ord_no": order_id,
        "subaction": "choose_order",
        "choose_order_subaction": "show_contract_details"
    }
    session.post(url, headers=headers, data=data, verify=False)
    data = {
        "sess_id": sess_id,
        "subaction": "kc2_security_password_get_token",
        "prefix": "kc2_customer_contract_details_extend_contract_",
        "password": password
    }
    f = session.post(url, headers=headers, data=data, verify=False)
    f.raise_for_status()
    if not json.loads(f.text)["rs"] == "success":
        return False
    token = json.loads(f.text)["token"]["value"]
    data = {
        "sess_id": sess_id,
        "ord_id": order_id,
        "subaction": "kc2_customer_contract_details_extend_contract_term",
        "token": token
    }
    session.post(url, headers=headers, data=data, verify=False)
    time.sleep(5)
    return True


def check(sess_id, session):
    print_("Checking.......")
    d = get_servers(sess_id, session)
    flag = True
    for key, val in d.items():
        if val:
            flag = False
            print_("ServerID: %s Renew Failed!" % key)
    if flag:
        print_("ALL Work Done! Enjoy")

# Server酱 http://sc.ftqq.com/?c=code
def server_chan():
    data = (
        ('text', 'EUserv续费日志'),
        ('desp', desp)
    )
    response = requests.post('https://sc.ftqq.com/' + SCKEY + '.send', data=data)
    if response.status_code != 200:
        print('Server酱 推送失败')
    else:
        print('Server酱 推送成功')

# 酷推 https://cp.xuthus.cc/
def CoolPush():
    c = 'EUserv续费日志\n\n' + desp
    data = json.dumps({'c': c})
    url = 'https://push.xuthus.cc/' + CoolPush_MODE + '/' + CoolPush_Skey
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print('酷推 推送失败')
    else:
        print('酷推 推送成功')

# PushPlus https://pushplus.hxtrip.com/message
def PushPlus():
    data = (
        ('token', PushPlus_Token),
        ('title', 'EUserv续费日志'),
        ('content', desp)
    )
    url = 'http://pushplus.hxtrip.com/send'
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print('PushPlus 推送失败')
    else:
        print('PushPlus 推送成功')

def main_handler(event, context):
    if not USERNAME or not PASSWORD:
        print_("你没有添加任何账户")
        exit(1)
    user_list = USERNAME.strip().split()
    passwd_list = PASSWORD.strip().split()
    if len(user_list) != len(passwd_list):
        print_("The number of usernames and passwords do not match!")
        exit(1)
    for i in range(len(user_list)):
        print('*' * 30)
        print_("正在续费第 %d 个账号" % (i + 1))
        sessid, s = login(user_list[i], passwd_list[i])
        if sessid == '-1':
            print_("第 %d 个账号登陆失败，请检查登录信息" % (i + 1))
            continue
        SERVERS = get_servers(sessid, s)
        print_("检测到第 {} 个账号有 {} 台VPS，正在尝试续期".format(i + 1, len(SERVERS)))
        for k, v in SERVERS.items():
            if v:
                if not renew(sessid, s, passwd_list[i], k):
                    print_("ServerID: %s Renew Error!" % k)
                else:
                    print_("ServerID: %s has been successfully renewed!" % k)
            else:
                print_("ServerID: %s does not need to be renewed" % k)
        time.sleep(15)
        check(sessid, s)
        time.sleep(5)
    
    # 三个通知渠道至少选取一个
    SCKEY and server_chan()
    CoolPush_MODE and CoolPush_Skey and CoolPush()
    PushPlus_Token and PushPlus()
    
    print('*' * 30)
