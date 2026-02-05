import os
import requests
from bs4 import BeautifulSoup
import datetime

# ================= 配置区域 (WxPusher版) =================
# 从环境变量读取 Token 和 UID
WXPUSHER_TOKEN = os.environ.get("WXPUSHER_TOKEN")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID")
# =======================================================

def get_weather():
    """
    爬虫函数：抓取成都天气 (代码逻辑不变)
    """
    print("🕷️ 正在爬取天气数据...")
    url = "http://www.weather.com.cn/weather/101270101.shtml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        today_node = soup.find('li', class_='sky skyid lv2 on')
        date = today_node.find('h1').text
        weather = today_node.find('p', class_='wea').text
        high_temp = today_node.find('span').text if today_node.find('span') else ""
        low_temp = today_node.find('i').text
        wind = today_node.find('p', class_='win').find('i').text

        # WxPusher 支持 Markdown，我们可以把字变漂亮点
        # <br> 是换行，**文字** 是加粗
        report = f"""
📅 **日期**：{date}
🌍 **城市**：成都 (UESTC)
🌤️ **天气**：{weather}
🌡️ **温度**：{low_temp} ~ {high_temp}
🌬️ **风力**：{wind}

<span style="color:grey;font-size:12px">来自 GitHub Actions 自动播报</span>
        """
        return report

    except Exception as e:
        print(f"❌ 爬虫出错了: {e}")
        return None

def send_wxpusher(content):
    """
    使用 WxPusher 发送消息
    """
    print("🚀 正在通过 WxPusher 发送...")
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    data = {
        "appToken": WXPUSHER_TOKEN,
        "content": content,
        "summary": "📅 每日天气提醒",  # 这是消息卡片上显示的标题
        "contentType": 2,             # 2 表示 HTML/Markdown 格式
        "uids": [WXPUSHER_UID]        # 发送目标
    }
    
    try:
        res = requests.post(url, json=data).json()
        if res['success']:
            print("✅ 发送成功！")
        else:
            print(f"❌ 发送失败: {res['msg']}")
    except Exception as e:
        print(f"❌ 请求错误: {e}")

if __name__ == "__main__":
    # 1. 爬数据
    weather_info = get_weather()
    
    # 2. 如果爬到了，就发
    if weather_info:
        print("-" * 30)
        print(weather_info)
        print("-" * 30)
        send_wxpusher(weather_info)
    else:
        print("今天爬虫罢工了，没获取到数据。")
