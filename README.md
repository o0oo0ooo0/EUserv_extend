# EUserv_extend
使用 腾讯云函数 自动续期EUserv免费IPv6 VPS脚本

## 说明

自动获取账号内所有的VPS项目，并检测是否需要续期，需要续期会自动续期。

## 使用说明

1、修改 **main.py** 中的用户名和密码

```
USERNAME: 你的EUserv账户邮箱或Customer ID
PASSWORD: 账户的密码
```

2、新建层 **BeautifulSoup** 将 [BeautifulSoup.zip](https://github.com/o0oo0ooo0/EUserv_extend/raw/main/BeautifulSoup.zip) 导入 ，添加运行环境 Python 3.6。

3、新建腾讯云函数 **EUserv_extend** ，运行环境选择 Python 3.6，将修改后的 **main.py** 粘贴进去。

4、在 EUserv_extend⇨函数管理⇨层管理 里绑定层 **BeautifulSoup**。

5、测试，没有错误就在 EUserv_extend⇨触发管理⇨创建触发器触发周期⇨自定义触发周期 填入

```
0 0 12 * * * * //每天 12 点执行，修改成你想要的时间。
```
6、完成。

## 其他说明

本项目直接修改自 https://github.com/CokeMine/EUserv_extend 以适用于腾讯云函数。
