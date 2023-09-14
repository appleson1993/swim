from flask import Flask, render_template, request
import os, time, requests

# 設置檔
set_timeout_time = os.getenv('set_timeout_time')
set_timeout_to_fail = os.getenv('set_timeout_to_fail')
set_warnlineopen  = os.getenv('set_warnlineopen')
token = os.getenv('token')
# 手環資料存放
mac_list = []
status = []
pinglist = []
warn = []
times = []
warntime = []
last_update = []
timeout = []
count = []
# 初始化變數
ok, fail = 0, 0
msg = "null"
btn_count = 0

app = Flask(__name__)

def warnline(mac):
    if set_warnlineopen == '1':
        # 要發送的訊息
        message = '手環用戶發生狀況，請派人了解。' + "使用者MAC地址" + mac
        # HTTP 標頭參數與資料
        headers = {"Authorization": "Bearer " + token}
        data = {'message': message}
        # 以 requests 發送 POST 請求
        send = requests.post("https://notify-api.line.me/api/notify",
                      headers=headers, data=data)
        print(send.text)
def wirteenv(old, new):
    # 改寫env文件裡的變數set_timeout_to_fail的值
    with open('.env', 'r') as f:
        lines = f.readlines()
    with open('.env', 'w') as f_w:
        for line in lines:
            if line.split('=')[0] == old:
                line = old.split('=')[0] + "=" + new
            f_w.write(line)


@app.route('/')
def index():
    global ok, fail
    ok, fail = 0, 0
    try:
        for i in range(0, btn_count):
            if status[i] == 'ok':
                ok += 1
            else:
                fail += 1
    except:
        print('錯誤')
    return render_template('index.html', msg=msg, btn_count=btn_count, status=status, mac_list=mac_list,
                           pinglist=pinglist, fail=fail, ok=ok, warn=warn, times=times)


@app.route('/api/data_update', methods=['GET'])
def getdata():
    if request.args.get('mac_addr') and request.args.get('ip_addr') and request.args.get('status') != None:
        global btn_count
        mac_addr = request.args.get('mac_addr')
        ip_addr = request.args.get('ip_addr')
        get_status = request.args.get('status')
        ct = request.args.get('ct')
        '創一個陣列放入mac_addr'
        if mac_addr in mac_list and ip_addr in pinglist:
            status[mac_list.index(mac_addr)] = get_status
            last_update[mac_list.index(mac_addr)] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            timeout[mac_list.index(mac_addr)] = time.time()
            count[mac_list.index(mac_addr)] = ct
            if get_status == 'fail':
                warn[mac_list.index(mac_addr)] += 1
                warntime[mac_list.index(mac_addr)] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        if mac_addr not in mac_list and ip_addr not in pinglist:
            '把mac_addr和ip_addr放入mac_list'
            mac_list.append(mac_addr)
            pinglist.append(ip_addr)
            status.append(get_status)
            count.append(ct)
            # 取得現在時間
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            times.append(now)
            timeout.append(time.time())
            last_update.append(now)
            if get_status == 'fail':
                warn.append(1)
                warntime.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            else:
                warn.append(0)
                warntime.append('')

            btn_count += 1

        if get_status == 'fail':
            warnline(mac_addr)

        return (str(pinglist) + str(mac_list) + str(status))
    else:
        return 'no data'
    return "no query"


datas = []
dataload = []
@app.route('/api/haha', methods=['GET'])
def haha():
    global dataload
    if request.args.get('data'):
        data = request.args.get('data')
        datas.append(data)

        try:
            dataload = datas[-1]
        except:
            dataload = datas

    return dataload

@app.route('/api/hahaf', methods=['GET'])
def hahaf():
    return render_template('haha.html')


# @app.route('/api/test', methods=['GET'])
# def test():
#     pinok = []
#     pinfail = []
#     for i in pinglist:
#         ping = os.system('ping -c 1 -t 1 ' + i)
#         if ping == 0:
#             print('ping ok' + i)
#             pinok.append(i)
#         else:
#             print('ping fail' + i)
#             pinfail.append(i)
#
#     return "失敗" + str(pinfail) + "成功" + str(pinok)


@app.route('/button')
def button():
    for i in range(0, btn_count):
        if time.time() - timeout[i] > int(set_timeout_time):
            status[i] = 'warn'

            if time.time() - timeout[i] > int(set_timeout_to_fail):
                status[i] = 'fail'
                warnline(mac_list[i])

    return render_template('button.html', msg=msg, btn_count=btn_count, status=status, mac_list=mac_list,
                           pinglist=pinglist, warn=warn, times=times, warntime=warntime, last_update=last_update , count = count)


@app.route('/api/cancel', methods=['GET'])
def cancel():
    global cid

    if request.args.get('id') != None:
        cid = request.args.get('id')
        status[int(cid)] = 'ok'
        return "取消：" + cid
    else:
        return 'no data'

if __name__ == '__main__':
    app.run(debug=True, port=8000)


#幫我印出你好

