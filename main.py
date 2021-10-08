# -*- coding: utf8 -*-
import re
import json
import time
import requests
from bs4 import BeautifulSoup

import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPDataError


# 强烈建议部署在非大陆区域，例如HK、SG等
# 常量命名使用全部大写的方式，可以使用下划线。
USERNAME = ''  # 这里填用户名，邮箱也可
PASSWORD = ''  # 这里填密码

# TrueCaptcha https://apitruecaptcha.org
# https://gist.github.com/ZetaoYang/e182453efadc90739a14daf2bd829087
# 验证码识别，默认使用 Demo API，每天有100次免费额度，建议自行注册以确保稳定性
TRUECAPTCHA_USERID = 'arun56'
TRUECAPTCHA_APIKEY = 'wMjXmBIcHcdYqO2RrsVN'
TRUECAPTCHA_CHECK_USAGE = True

# Server酱 http://sc.ftqq.com/?c=code
SCKEY = ''  # 这里填Server酱的key，无需推送可不填 示例: SCU646xxxxxxxxdacd6a5dc3f6

# 酷推 https://cp.xuthus.cc
COOL_PUSH_SKEY = ''
# 通知类型 CoolPush_MODE的可选项有（默认send）：send[QQ私聊]、group[QQ群聊]、wx[个微]、ww[企微]
COOL_PUSH_MODE = 'send'

# PushPlus https://pushplus.hxtrip.com/message
PUSH_PLUS_TOKEN = ''

# Telegram Bot Push https://core.telegram.org/bots/api#authorizing-your-bot
TG_BOT_TOKEN = ''  # 通过 @BotFather 申请获得，示例：1077xxx4424:AAFjv0FcqxxxxxxgEMGfi22B4yh15R5uw
TG_USER_ID = ''  # 用户、群组或频道 ID，示例：129xxx206
TG_API_HOST = 'api.telegram.org'  # 自建 API 反代地址，供网络环境无法访问时使用，网络正常则保持默认

# wecomchan https://github.com/easychen/wecomchan
WECOMCHAN_DOMAIN = ''  # http(s)://example.com/
WECOMCHAN_SEND_KEY = ''
WECOMCHAN_TO_USER = '@all'  # 默认全部推送, 对个别人推送可用 User1|User2
# 变量命名使用全部小写的方式，可以使用下划线。
desp = ''  # 不用动


# 函数命名使用全部小写的方式，可以使用下划线。
def print_(info):
    print(info)
    global desp
    desp = desp + info + '\n\n'


def login(username, password) -> (str, requests.session):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36",
        "origin": "https://www.euserv.com",
    }
    url = "https://support.euserv.com/index.iphp"
    captcha_image_url = "https://support.euserv.com/securimage_show.php"
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
    f = session.post(url, headers=headers, data=login_data)
    f.raise_for_status()

    if (
        f.text.find("Hello") == -1
        and f.text.find("Confirm or change your customer data here") == -1
    ):
        if (
            f.text.find(
                "To finish the login process please solve the following captcha."
            )
            == -1
        ):
            return "-1", session
        else:
            print_("[Captcha Solver] 进行验证码识别...")
            solved_result = captcha_solver(captcha_image_url, session)
            captcha_code = handle_captcha_solved_result(solved_result)
            print_("[Captcha Solver] 识别的验证码是: {}".format(captcha_code))
            if TRUECAPTCHA_CHECK_USAGE:
                usage = get_captcha_solver_usage()
                print_(
                    "[Captcha Solver] current date {0} api usage count: {1}".format(
                        usage[0]["date"], usage[0]["count"]
                    )
                )
            f2 = session.post(
                url,
                headers=headers,
                data={
                    "subaction": "login",
                    "sess_id": sess_id,
                    "captcha_code": captcha_code,
                },
            )
            if (
                f2.text.find(
                    "To finish the login process please solve the following captcha."
                )
                == -1
            ):
                print_("[Captcha Solver] 验证通过")
                return sess_id, session
            else:
                print_("[Captcha Solver] 验证失败")
                return "-1", session
    else:
        return sess_id, session

def login_retry(*args, **kwargs):
    def wrapper(func):
        def inner(username, password):
            ret, ret_session = func(username, password)
            max_retry = kwargs.get("max_retry")
            # default retry 3 times
            if not max_retry:
                max_retry = 3
            number = 0
            if ret == "-1":
                while number < max_retry:
                    number += 1
                    if number > 1:
                        print_("[EUserv] Login tried the {}th time".format(number))
                    sess_id, session = func(username, password)
                    if sess_id != "-1":
                        return sess_id, session
                    else:
                        if number == max_retry:
                            return sess_id, session
            else:
                return ret, ret_session
        return inner
    return wrapper

def get_servers(sess_id: str, session: requests.session) -> {}:
    d = {}
    url = "https://support.euserv.com/index.iphp?sess_id=" + sess_id
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36",
        "origin": "https://www.euserv.com"
    }
    f = session.get(url=url, headers=headers)
    f.raise_for_status()
    soup = BeautifulSoup(f.text, 'html.parser')
    for tr in soup.select('#kc2_order_customer_orders_tab_content_1 .kc2_order_table.kc2_content_table tr'):
        server_id = tr.select('.td-z1-sp1-kc')
        if not len(server_id) == 1:
            continue
        flag = (
            True
            if tr.select(".td-z1-sp2-kc .kc2_order_action_container")[0]
            .get_text()
            .find("Contract extension possible from")
            == -1
            else False
        )
        d[server_id[0].get_text()] = flag
    return d


def renew(sess_id: str, session: requests.session, password: str, order_id: str) -> bool:
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
    session.post(url, headers=headers, data=data)
    data = {
        "sess_id": sess_id,
        "subaction": "kc2_security_password_get_token",
        "prefix": "kc2_customer_contract_details_extend_contract_",
        "password": password
    }
    f = session.post(url, headers=headers, data=data)
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
    session.post(url, headers=headers, data=data)
    time.sleep(5)
    return True


def check(sess_id: str, session: requests.session):
    print("Checking.......")
    d = get_servers(sess_id, session)
    flag = True
    for key, val in d.items():
        if val:
            flag = False
            print_("ServerID: %s Renew Failed!" % key)
    if flag:
        print_("ALL Work Done! Enjoy")
        

# TrueCaptcha https://apitruecaptcha.org
def captcha_solver(captcha_image_url: str, session: requests.session) -> dict:
    response = session.get(captcha_image_url)
    encoded_string = base64.b64encode(response.content)
    url = "https://api.apitruecaptcha.org/one/gettext"

    data = {
        "userid": TRUECAPTCHA_USERID,
        "apikey": TRUECAPTCHA_APIKEY,
        "case": "mixed",
        "mode": "human",
        "data": str(encoded_string)[2:-1],
    }
    r = requests.post(url=url, json=data)
    j = json.loads(r.text)
    return j

def handle_captcha_solved_result(solved: dict) -> str:
    if "result" in solved:
        solved_text = solved["result"]
        if "RESULT  IS" in solved_text:
            print_("[Captcha Solver] You are using the demo apikey.")
            print("There is no guarantee that demo apikey will work in the future!")
            # because using demo apikey
            text = re.findall(r"RESULT  IS . (.*) .", solved_text)[0]
        else:
            # using your own apikey
            print_("[Captcha Solver] You are using your own apikey.")
            text = solved_text
        operators = ["X", "x", "+", "-"]
        if any(x in text for x in operators):
            for operator in operators:
                operator_pos = text.find(operator)
                if operator == "x" or operator == "X":
                    operator = "*"
                if operator_pos != -1:
                    left_part = text[:operator_pos]
                    right_part = text[operator_pos + 1 :]
                    if left_part.isdigit() and right_part.isdigit():
                        return eval(
                            "{left} {operator} {right}".format(
                                left=left_part, operator=operator, right=right_part
                            )
                        )
                    else:
                        # Because these symbols("X", "x", "+", "-") do not appear at the same time,
                        # it just contains an arithmetic symbol.
                        return text
        else:
            return text
    else:
        print(solved)
        raise KeyError("Failed to find parsed results.")

def get_captcha_solver_usage() -> dict:
    url = "https://api.apitruecaptcha.org/one/getusage"
    params = {
        "username": TRUECAPTCHA_USERID,
        "apikey": TRUECAPTCHA_APIKEY,
    }
    r = requests.get(url=url, params=params)
    j = json.loads(r.text)
    return j


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
def coolpush():
    c = 'EUserv续费日志\n\n' + desp
    data = json.dumps({'c': c})
    url = 'https://push.xuthus.cc/' + COOL_PUSH_MODE + '/' + COOL_PUSH_SKEY
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print('酷推 推送失败')
    else:
        print('酷推 推送成功')


# PushPlus https://pushplus.hxtrip.com/message
def push_plus():
    data = (
        ('token', PUSH_PLUS_TOKEN),
        ('title', 'EUserv续费日志'),
        ('content', desp)
    )
    url = 'https://pushplus.hxtrip.com/send'
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print('PushPlus 推送失败')
    else:
        print('PushPlus 推送成功')


# Telegram Bot Push https://core.telegram.org/bots/api#authorizing-your-bot
def telegram():
    data = (
        ('chat_id', TG_USER_ID),
        ('text', 'EUserv续费日志\n\n' + desp)
    )
    response = requests.post('https://' + TG_API_HOST + '/bot' + TG_BOT_TOKEN + '/sendMessage', data=data)
    if response.status_code != 200:
        print('Telegram Bot 推送失败')
    else:
        print('Telegram Bot 推送成功')


# wecomchan https://github.com/easychen/wecomchan
def wecomchan():
    response = requests.get(WECOMCHAN_DOMAIN + 'wecomchan?sendkey=' + WECOMCHAN_SEND_KEY + '&msg_type=text' + '&to_user=' +
                            WECOMCHAN_TO_USER + '&msg=' + 'EUserv续费日志\n\n' + desp)
    if response.status_code != 200:
        print('wecomchan 推送失败')
    else:
        print('wecomchan 推送成功')


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
        servers = get_servers(sessid, s)
        print_("检测到第 {} 个账号有 {} 台VPS，正在尝试续期".format(i + 1, len(servers)))
        for k, v in servers.items():
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

    # 五个通知渠道至少选取一个
    SCKEY and server_chan()
    COOL_PUSH_MODE and COOL_PUSH_SKEY and coolpush()
    PUSH_PLUS_TOKEN and push_plus()
    TG_BOT_TOKEN and TG_USER_ID and TG_API_HOST and telegram()
    WECOMCHAN_DOMAIN and WECOMCHAN_SEND_KEY and WECOMCHAN_TO_USER and wecomchan()

    print('*' * 30)


if __name__ == '__main__':  # 方便我本地调试
    main_handler(None, None)
