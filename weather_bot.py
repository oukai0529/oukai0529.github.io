import os
import requests
from bs4 import BeautifulSoup
import datetime

# ================= 配置区域 (群机器人版) =================
# 从环境变量读取 Webhook URL
WEBHOOK_URL = os.environ.get("WECHAT_WEBHOOK_URL")
# =======================================================

def get_weather():
    """
    爬虫函数：抓取成都天气
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

        # 群机器人支持 Markdown 格式
        # <font color="info">绿色</font> <font color="comment">灰色</font> <font color="warning">橙红色</font>
        report = f"""### 📅 成都天气日报
> 日期：<font color="comment">{date}</font>
> 城市：<font color="info">成都 (UESTC)</font>
> 天气：**{weather}**
> 温度：<font color="warning">{low_temp} ~ {high_temp}</font>
> 风力：{wind}

<font color="comment">By GitHub Actions</font>"""
        return report

    except Exception as e:
        print(f"❌ 爬虫出错了: {e}")
        return None

def send_group_bot(content):
    """
    使用群机器人 Webhook 发送
    """
    print("🚀 正在请求群机器人接口...")
    
    if not WEBHOOK_URL:
        print("❌ 错误：未找到 Webhook URL，请检查 GitHub Secrets！")
        return

    # 构造数据包
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    
    try:
        # 直接 POST 那个长链接，不需要 Token
        res = requests.post(WEBHOOK_URL, json=data).json()
        if res['errcode'] == 0:
            print("✅ 发送成功！")
        else:
            print(f"❌ 发送失败: {res['errmsg']}")
    except Exception as e:
        print(f"❌ 请求错误: {e}")

if __name__ == "__main__":
    weather_info = get_weather()
    if weather_info:
        send_group_bot(weather_info)
    else:
        print("没爬到数据")
