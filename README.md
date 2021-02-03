# EUserv_extend
使用 [腾讯云函数 SCF](https://console.cloud.tencent.com/scf/) 自动续期EUserv免费IPv6 VPS脚本

## 说明

自动获取账号内所有的VPS项目，并检测是否需要续期，需要续期会自动续期。

## 使用说明

1、修改 **main.py** 中的用户名，密码和 [Server酱](https://sc.ftqq.com/?c=code) 或者 [酷推](https://cp.xuthus.cc) 或者 [PushPlus](https://pushplus.hxtrip.com/message) 的key


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
Server酱

```
SCKEY = 'SCU64664Tfb2052dc10382535c3dd19e48ba000fc5dacd6a5dc3f6'
```
酷推

```
CoolPush_Skey = ''
# 通知类型 CoolPush_MODE的可选项有（默认send）：send[QQ私聊]、group[QQ群聊]、wx[个微]、ww[企微]
CoolPush_MODE = 'send'
```
PushPlus

```
PushPlus_Token = ''
```

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
