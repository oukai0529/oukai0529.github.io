import os  # <--- 确保这一行在最上面

# ================= 配置区域 (修改版) =================
# 从环境变量中读取密钥 (这样最安全)
CORP_ID = os.environ.get("CORP_ID")
CORP_SECRET = os.environ.get("CORP_SECRET")
AGENT_ID = os.environ.get("AGENT_ID")
# ===================================================

def get_weather():
    """
    爬虫函数：去中国天气网抓取成都的天气
    """
    print("🕷️ 正在爬取天气数据...")
    
    # 1. 目标网址 (成都的代码是 101270101，你可以换成西安 101110101)
    url = "http://www.weather.com.cn/weather/101270101.shtml"
    
    # 2. 伪装成浏览器 (反爬虫)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        # 3. 发送请求
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8' # 处理中文乱码
        
        # 4. 解析网页 (BeautifulSoup 出场)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # --- 数据提取逻辑 (这是网页分析的核心) ---
        # 找到包含今天天气的那个 div (页面上第一个 li class="sky skyid lv2 on")
        today_node = soup.find('li', class_='sky skyid lv2 on')
        
        # 提取日期
        date = today_node.find('h1').text
        # 提取天气状况 (比如 "多云")
        weather = today_node.find('p', class_='wea').text
        # 提取温度 (最高/最低)
        high_temp = today_node.find('span').text if today_node.find('span') else ""
        low_temp = today_node.find('i').text
        # 提取风力
        wind = today_node.find('p', class_='win').find('i').text

        # 5. 组装成一段人话
        report = f"""
📅 日期：{date}
🌍 城市：成都 (UESTC)
🌤️ 天气：{weather}
🌡️ 温度：{low_temp} ~ {high_temp}
🌬️ 风力：{wind}

(来自 Python 爬虫自动播报)
        """
        return report

    except Exception as e:
        print(f"❌ 爬虫出错了: {e}")
        return None

def send_wechat(content):
    """
    发送函数：把内容推送到微信
    """
    print("🚀 正在发送微信消息...")
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={CORP_SECRET}"
    try:
        token = requests.get(token_url).json()['access_token']
        send_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
        data = {
            "touser": "@all",
            "msgtype": "text",
            "agentid": AGENT_ID,
            "text": {"content": content},
            "safe": 0
        }
        res = requests.post(send_url, json=data).json()
        if res['errcode'] == 0:
            print("✅ 发送成功！")
        else:
            print(f"❌ 发送失败: {res['errmsg']}")
    except Exception as e:
        print(f"❌ 发送流程出错: {e}")

# --- 主程序入口 ---
if __name__ == "__main__":
    # 1. 爬数据
    weather_info = get_weather()
    
    # 2. 如果爬到了，就发微信
    if weather_info:
        print("-" * 30)
        print(weather_info) # 在终端也打印一下方便看
        print("-" * 30)
        send_wechat(weather_info)
    else:
        print("今天爬虫罢工了，没获取到数据。")