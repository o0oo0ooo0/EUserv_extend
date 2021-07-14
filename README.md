# EUserv_extend
使用 [腾讯云函数 SCF](https://console.cloud.tencent.com/scf/) 自动续期EUserv免费IPv6 VPS脚本

## 说明

自动获取账号内所有的VPS项目，并检测是否需要续期，需要续期会自动续期。

## 使用说明

1、修改 **main.py** 中的用户名，密码，并配置合适的推送方式（[Server酱](https://sc.ftqq.com/?c=code)、[酷推](https://cp.xuthus.cc)、[PushPlus](https://pushplus.hxtrip.com/message)、[Telegram Bot Push](https://core.telegram.org/bots/api#authorizing-your-bot) 或 [wecomchan](https://github.com/easychen/wecomchan)）


USERNAME: 你的EUserv账户邮箱或Customer ID

```
USERNAME = 'user@gmail.com'
USERNAME = 'user1@gmail.com user2@gmail.com' # 多个账号写法
```
PASSWORD: 账户的密码

```
PASSWORD = 'password'
PASSWORD = 'password1 password2' # 多个账号写法
```
<details>
  <summary>Server酱</summary>
  <pre><code> 
SCKEY = 'SCU64664Tfb2052dc10382535c3dd19e48ba000fc5dacd6a5dc3f6'
  </code></pre>
</details>

<details>
  <summary>酷推</summary>
<pre><code> 
COOLPUSH_SKEY = ''
# 通知类型 CoolPush_MODE的可选项有（默认send）：send[QQ私聊]、group[QQ群聊]、wx[个微]、ww[企微]
COOLPUSH_MODE = 'send'
</code></pre>
</details>

<details>
  <summary>PushPlus</summary>
<pre><code> 
PUSHPLUS_TOKEN = ''
</code></pre>
</details>

<details>
  <summary>Telegram Bot Push</summary>
<pre><code> 
TG_BOT_TOKEN = '' # 通过 @BotFather 申请获得，示例：1077xxx4424:AAFjv0FcqxxxxxxgEMGfi22B4yh15R5uw
TG_USER_ID = '' # 用户、群组或频道 ID，示例：129xxx206
TG_API_HOST = 'api.telegram.org' # 自建 API 反代地址，供网络环境无法访问时使用，网络正常则保持默认
</code></pre>
</details>

<details>
  <summary>wecomchan</summary>
具体可参考 https://github.com/easychen/wecomchan/tree/main/go-scf
<pre><code> 
WECOMCHAN_DOMAIN = ''  # 你的服务器的主页 例: https://example.com/
WECOMCHAN_SEND_KEY = ''  # 你配置的key
WECOMCHAN_TO_USER = '@all'  # 默认全部推送, 对个别人推送可用 User1|User2
</code></pre>
</details>

2、新建层 **BeautifulSoup** 将 [BeautifulSoup.zip](https://github.com/o0oo0ooo0/EUserv_extend/releases/download/0.1/BeautifulSoup.zip) 导入 ，添加运行环境 Python 3.6。

3、新建腾讯云函数 **EUserv_extend** ，运行环境选择 Python 3.6，创建方式选择 空白函数，内存选择 64M，执行超时时间建议为 300 s（网站在国外访问比较慢，建议部署在非大陆区域，例如HK、SG等），将修改后的 **main.py** 粘贴进去。

4、在 EUserv_extend⇨函数管理⇨层管理 里绑定层 **BeautifulSoup**。

5、测试，没有错误就在 EUserv_extend⇨触发管理⇨创建触发器触发周期⇨自定义触发周期 填入

```
0 0 8 */7 * * * # 每 7 天的 8 点执行，修改成你想要的时间。Cron 相关文档: https://cloud.tencent.com/document/product/583/9708
```
6、完成。

## 其他说明

本项目直接修改自 [CokeMine/EUserv_extend](https://github.com/CokeMine/EUserv_extend) 以适用于腾讯云函数。
