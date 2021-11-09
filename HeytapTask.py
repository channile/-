# 基于 @hwkxk(丶大K丶) 的欢太签到脚本修改
# 去除日志输出、控制台输出
# 可在腾讯云函数上运行

import requests,time,traceback,configparser

#用户登录全局变量
client = None
session = None

# 读取用户信息
def readConfig():
    try:
        global userconfig
        userconfig = configparser.RawConfigParser()
        path = "./config.ini"
        userconfig.read(path, encoding="utf-8")
        return userconfig
        # print(userconfig.sections())
        # print(userconfig.options('config'))
        # print(userconfig.get('config','cookies'))
    except Exception as e:
        print(traceback.format_exc())

def get_userinfo(HT_cookies,HT_UA):
    flag = False
    global session
    session = requests.Session()
    headers = {
        'Host': 'www.heytap.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': HT_UA,
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'cookie': HT_cookies
    }
    response = session.get('https://www.heytap.com/cn/oapi/users/web/member/info', headers=headers)
    response.encoding="utf-8"

    try:
        result = response.json()
        if result['code'] == 200:
            print('【登录成功】: ' + result['data']['realName'])
            flag = True
        else:
            print('【登录失败】: ' + result['errorMessage'])
    except Exception as e:
        print(traceback.format_exc())

    if flag:
        return session
    else:
        return False

# 任务中心
def taskCenter():
    headers = {
        'Host': 'store.oppo.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': HT_UserAgent,
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'cookie': HT_cookies,
        'referer': 'https://store.oppo.com/cn/app/taskCenter/index'
    }
    res1 = client.get('https://store.oppo.com/cn/oapi/credits/web/credits/show', headers=headers)
    res1 = res1.json()
    # print(res1)
    return res1

# 每日签到
def dailySign():
    try:
        date = time.strftime("%Y-%m-%d")
        headers = {
        'Host': 'store.oppo.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': HT_UserAgent,
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'cookie': HT_cookies,
        'referer': 'https://store.oppo.com/cn/app/taskCenter/index'
        }
        res = taskCenter()
        status = res['data']['userReportInfoForm']['status']
        if status == 0:
            res = res['data']['userReportInfoForm']['gifts']
            for data in res:
                if data['date'] == date:
                    qd = data
            if qd['today'] == False:
                data = "amount=" + str(qd['credits'])
                res1 = client.post('https://store.oppo.com/cn/oapi/credits/web/report/immediately', headers=headers,data=data)
                res1 = res1.json()
                if res1['code'] == 200:
                    print('【每日签到成功】: ' + res1['data']['message'])
                else:
                    print('【每日签到失败】: ' + str(res1))
            else:
                print(str(qd['credits']),str(qd['type']),str(qd['gift']))
                if len(str(qd['type'])) < 1 :
                    data = "amount=" + str(qd['credits'])
                else:
                    data = "amount=" + str(qd['credits']) + "&type=" + str(qd['type']) + "&gift=" + str(qd['gift'])
                res1 = client.post('https://store.oppo.com/cn/oapi/credits/web/report/immediately',  headers=headers,data=data)
                res1 = res1.json()
                if res1['code'] == 200:
                    print('【每日签到成功】: ' + res1['data']['message'])
                else:
                    print('【每日签到失败】: ' + str(res1))
        else:
            print('【每日签到】: 已经签到过了！')
        time.sleep(1)
    except Exception as e:
        print(traceback.format_exc())
        print('【每日签到】: 错误，原因为: ' + str(e))

# 浏览商品
def dailyLook():
    try:
        headers = {
            'clientPackage': 'com.oppo.store',
            'Host': 'msec.opposhop.cn',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'User-Agent': 'okhttp/3.12.12.200sp1',
            'Accept-Encoding': 'gzip',
            'cookie': HT_cookies,
        }
        res = taskCenter()
        res = res['data']['everydayList']
        for data in res:
            if data['name'] == '浏览商品':
                qd = data
        if qd['completeStatus'] == 0:
            shopList = client.get('https://msec.opposhop.cn/goods/v1/SeckillRound/goods/115?pageSize=12&currentPage=1')
            res = shopList.json()
            if res['meta']['code'] == 200:
                for skuinfo in res['detail']:
                    skuid = skuinfo['skuid']
                    print('正在浏览商品ID：', skuid)
                    client.get('https://msec.opposhop.cn/goods/v1/info/sku?skuId=' + str(skuid), headers=headers)
                    time.sleep(5)

                res2 = cashingCredits(qd['marking'], qd['type'], qd['credits'])
                if res2 == True:
                    print('【每日浏览商品】: ' + '任务完成！积分领取+' + str(qd['credits']))
                else:
                    print('【每日浏览商品】: ' + "领取积分奖励出错！")
            else:
                print('【每日浏览商品】: ' + '错误，获取商品列表失败')
        elif qd['completeStatus'] == 1:
            res2 = cashingCredits(qd['marking'], qd['type'], qd['credits'])
            if res2 == True:
                print('【每日浏览商品】: ' + '任务完成！积分领取+' + str(qd['credits']))
            else:
                print('【每日浏览商品】: ' + '领取积分奖励出错！')
        else:
            print('【每日浏览商品】: ' + '任务已完成！')
    except Exception as e:
        print(traceback.format_exc())
        print('【每日签到】: 错误，原因为: ' + str(e))

# 每日分享
def dailyShare():
    try:
        headers = {
        'clientPackage': 'com.oppo.store',
        'Host': 'msec.opposhop.cn',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': 'okhttp/3.12.12.200sp1',
        'Accept-Encoding': 'gzip',
        'cookie': HT_cookies,
        }
        daySignList = taskCenter()
        res = daySignList
        res = res['data']['everydayList']
        for data in res:
            if data['name'] == '分享商品到微信':
                qd = data
        if qd['completeStatus'] == 0:
            count = qd['readCount']
            endcount = qd['times']
            while (count <= endcount):
                client.get('https://msec.opposhop.cn/users/vi/creditsTask/pushTask?marking=daily_sharegoods', headers=headers)
                count += 1
            res2 = cashingCredits(qd['marking'],qd['type'],qd['credits'])
            if res2 == True:
                print('【每日分享商品】: ' + '任务完成！积分领取+' + str(qd['credits']))
            else:
                print('【每日分享商品】: ' + '领取积分奖励出错！')
        elif qd['completeStatus'] == 1:
            res2 = cashingCredits(qd['marking'],qd['type'],qd['credits'])
            if res2 == True:
                print('【每日分享商品】: ' + '任务完成！积分领取+' + str(qd['credits']))
            else:
                print('【每日分享商品】: ' + '领取积分奖励出错！')
        else:
            print('【每日分享商品】: ' + '任务已完成！')
    except Exception as e:
        print(traceback.format_exc())
        print('【每日分享商品】: 错误，原因为: ' + str(e))

# 领取积分
def cashingCredits(marking,type,credits):
    headers = {
        'Host': 'store.oppo.com',
        'clientPackage': 'com.oppo.store',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': HT_UserAgent,
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'cookie': HT_cookies,
        'Origin': 'https://store.oppo.com',
        'X-Requested-With': 'com.oppo.store',
        'referer': 'https://store.oppo.com/cn/app/taskCenter/index?us=gerenzhongxin&um=hudongleyuan&uc=renwuzhongxin'
    }

    data = "marking=" + str(marking) + "&type=" + str(type) + "&amount=" + str(credits)
    res = client.post('https://store.oppo.com/cn/oapi/credits/web/credits/cashingCredits', data=data, headers=headers)
    res = res.json()
    if res['code'] == 200:
        return True
    else:
        return False

def main():
    users = readConfig()
    global client
    global HT_cookies
    global HT_UserAgent
    HT_cookies = users.get('config','cookies')
    HT_UserAgent = users.get('config','User-Agent')
    # get_userinfo(HT_cookies,HT_UserAgent)

    client = get_userinfo(HT_cookies, HT_UserAgent)
    # taskCenter()

    if client:
        dailySign()
        dailyLook()
        dailyShare()

if __name__ == '__main__':
    main()