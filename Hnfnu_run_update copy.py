import requests
import json
import datetime  # 修改导入方式
import tkinter as tk
from tkinter import messagebox
from time import sleep
from tkinter import ttk
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64


def show_success_message(grade):
    root = tk.Tk()
    # 隐藏主窗口
    root.withdraw()
    # 弹出成功消息框
    messagebox.showinfo("成功", f"跑步成功，获得{grade}分！")


def show_error_message(err):
    root = tk.Tk()
    # 隐藏主窗口
    root.withdraw()
    # 弹出错误消息框
    messagebox.showerror("错误", err)


# 登录函数
def login(session, username, password):
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 12; V2344A Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Safari/537.36 uni-app Html5Plus/1.0 (Immersed/0.5714286)',
        'Content-Type': 'application/json',
        'Host': 'lb.hnfnu.edu.cn',
    }
    json_data = {
        'username': username,
        'password': password,
        'code': '',
        'uuid': '',
    }
    response = session.post('https://lb.hnfnu.edu.cn/login', headers=headers, json=json_data, verify=False)
    response_data = response.json()
    if response_data.get('code') == 500:
        err = '账号或密码错误'
        show_error_message(err)
        return None
    else:
        token = response_data.get('token')
        return f"Bearer {token}"

# 获取用户信息函数
def get_profile(session, bearer_token):
    headers = {
        'Authorization': bearer_token,
        'user-agent': 'Mozilla/5.0 (Linux; Android 12; V2344A Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Safari/537.36 uni-app Html5Plus/1.0 (Immersed/0.5714286)',
        'Host': 'lb.hnfnu.edu.cn',
    }
    response = session.get('https://lb.hnfnu.edu.cn/system/user/profile', headers=headers, verify=False)
    # print(response.text)

# 获取可打卡位置函数
def get_long_march_list(session, bearer_token):
    headers = {
        'Authorization': bearer_token,
        'user-agent': 'Mozilla/5.0 (Linux; Android 12; V2344A Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Safari/537.36 uni-app Html5Plus/1.0 (Immersed/0.5714286)',
        'Host': 'lb.hnfnu.edu.cn',
    }
    response = session.get('https://lb.hnfnu.edu.cn/school/student/LongMarchList', headers=headers, verify=False)
    # print(response.text)

# 获取信息函数
def get_info(session, bearer_token):
    headers = {
        'Authorization': bearer_token,
        'user-agent': 'Mozilla/5.0 (Linux; Android 12; V2344A Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Safari/537.36 uni-app Html5Plus/1.0 (Immersed/0.5714286)',
        'Host': 'lb.hnfnu.edu.cn',
    }
    response = session.get('https://lb.hnfnu.edu.cn/getInfo', headers=headers, verify=False)
    # print(response.text)

# 开始进入页面函数
def start_page(session, bearer_token, now):
    headers = {
        'Authorization': bearer_token,
        'user-agent': 'Mozilla/5.0 (Linux; Android 12; V2344A Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Safari/537.36 uni-app Html5Plus/1.0 (Immersed/0.5714286)',
        'Content-Type': 'application/json',
        'Host': 'lb.hnfnu.edu.cn',
    }
    # now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    json_data = {
        'dlatitude': '28.193135',
        'dlongitude': '112.865848',
       'startTime': formatted_time,
    }
    response = session.post('https://lb.hnfnu.edu.cn/school/student/addLMRanking', headers=headers, json=json_data, verify=False)
    return response.json().get('data')


# 加密函数
def encrypt_timestamp(custom_date=None):
    # 定义密钥并转换为字节类型
    key = "lanbu123456hndys".encode('utf-8')
    print(type(custom_date))
    try:
        if custom_date:
            # 解析自定义日期字符串为 datetime 对象
            if isinstance(custom_date, datetime.datetime):
                custom_date = custom_date.strftime("%Y-%m-%d %H:%M:%S")
            date = datetime.datetime.strptime(custom_date, "%Y-%m-%d %H:%M:%S")  # 修改这里
        else:
            # 如果未提供自定义日期，使用当前时间
            date = datetime.datetime.now()  # 修改这里
        print(type(date))
        # 获取时间戳并转换为字符串
        timestamp = str(int(date.timestamp() * 1000))

        # 格式化日期时间用于校验输出
        formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
        print("校验时间", formatted_date)

        # 创建 AES 加密器，使用 ECB 模式
        cipher = AES.new(key, AES.MODE_ECB)

        # 对时间戳进行填充并加密
        encrypted_bytes = cipher.encrypt(pad(timestamp.encode('utf-8'), AES.block_size))

        # 将加密结果转换为 Base64 编码的字符串，与 JavaScript 保持一致
        encrypted = base64.b64encode(encrypted_bytes).decode('utf-8')

        # 计算拆分索引
        split_index = (len(encrypted) + 1) // 2

        # 拆分加密结果
        header_part = encrypted[:split_index]
        body_part = encrypted[split_index:]

        return {
            'headerPart': header_part,
            'bodyPart': body_part
        }
    except ValueError:
        print("日期格式错误，请使用 'YYYY-MM-DD HH:MM:SS' 格式。")
        return None


# 提交信息函数
def submit_info(session, bearer_token, id, speed, mileage, now):
    duration_seconds = (mileage * 1000) / speed
    # now = datetime.datetime.now()
    new_time = now + datetime.timedelta(seconds=duration_seconds)
    formatted_time = new_time.strftime("%Y-%m-%d %H:%M:%S")

    total_seconds = round(duration_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    now_str = datetime.datetime.now()
    now_str = now_str.strftime("%Y-%m-%d %H:%M:%S")  # 将 datetime 对象转换为字符串
    result = encrypt_timestamp(now_str)

    headers = {
        'custom-header': result['headerPart'],
        'Authorization': bearer_token,
        'user-agent': 'Mozilla/5.0 (Linux; Android 12; V2344A Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Safari/537.36 uni-app Html5Plus/1.0 (Immersed/0.5714286)',
        'Content-Type': 'application/json',
        'Host': 'lb.hnfnu.edu.cn',
    }
    json_data = {
        'id': id,
       'state': '等待',
       'mileage': mileage,
       'mileageSum': mileage,
        'formattedTime': time_str,
        'overTime': formatted_time,
       'speed': speed,
        'bodyPart': result['bodyPart']
    }
    # show_progress_bar()
    sleep(5)

    response = session.post('https://lb.hnfnu.edu.cn/school/student/longMarchSpeed', headers=headers, json=json_data, verify=False)
    print(response.text)
    data_dict = json.loads(response.text)
    # 检查 'data' 键是否存在于字典中
    if 'data' in data_dict:
        data = data_dict['data']
        # 检查 'Grade' 键是否存在于 'data' 字典中
        if 'Grade' in data:
            grade = data['Grade']
            show_success_message(grade)
        else:
            err = "跑步失败"
            show_error_message(err)
    else:
        err = "跑步失败"
        show_error_message(err)

    return response.text


def main(username, password, speed, mileage):
    session = requests.Session()
    # 登录
    bearer_token = login(session, username, password)
    if bearer_token is None:
        exit()
    else:
        # 获取用户信息
        sleep(1)
        get_profile(session, bearer_token)
        # 获取可打卡位置
        sleep(1)
        get_long_march_list(session, bearer_token)
        # 获取信息
        sleep(1)
        get_info(session, bearer_token)
        # 开始进入页面
        sleep(1)
        now = datetime.datetime.now()
        id = start_page(session, bearer_token, now)
        print(id)
        # 提交信息
        # speed = 2.15  
        # mileage = 4.3
        result = submit_info(session, bearer_token, id, speed, mileage, now)
        print(result)


if __name__ == "__main__":
    expiration_date = datetime.datetime(2025, 7, 10)
    current_date = datetime.datetime.now()
    if current_date > expiration_date:
        print("404 请求错误")
    else:
        username = input("请输入账号：")
        password = input("请输入密码：")
        #speed = "{:.2f}".format(float(input("请输入大于1.50速度，两位小数：")))
        #mileage = "{:.1f}".format(float(input("请输入您的里程，一位小数：")))
        

        speed = 3.15  
        mileage = 4.3
        speed = float(speed)
        mileage = float(mileage)
        main(username, password, speed, mileage)