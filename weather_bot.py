import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# ================= 配置区域 =================
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
QWEATHER_KEY = os.environ.get("QWEATHER_KEY")  # 新增：和风天气的Key

# 接收人列表
RECEIVERS = ["2387993145@qq.com"] 

# 你的位置ID (成都成华区/电子科大附近)
# 你可以在 https://github.com/qweather/geo 查找更精确的 ID
# 101270101 是成都的通用 ID，通常够用了
LOCATION_ID = "101270101"
# ===========================================

def get_weather_data():
    """
    通过和风天气 API 获取详尽数据
    """
    print("📡 正在调用和风天气 API...")
    
    if not QWEATHER_KEY:
        print("❌ 错误：未找到 QWEATHER_KEY，请检查 GitHub Secrets")
        return None

    try:
        # 1. 获取【实时天气】 (温度、天气状况、风力、湿度、气压)
        # 免费版 API 域名是 devapi.qweather.com
        url_now = f"https://devapi.qweather.com/v7/weather/now?location={LOCATION_ID}&key={QWEATHER_KEY}"
        resp_now = requests.get(url_now).json()
        
        # 2. 获取【今天的天气预报】 (最高温、最低温、日出日落)
        url_daily = f"https://devapi.qweather.com/v7/weather/3d?location={LOCATION_ID}&key={QWEATHER_KEY}"
        resp_daily = requests.get(url_daily).json()
        
        # 3. 获取【生活指数】 (穿衣、紫外线、运动)
        # type=1(运动),3(穿衣),5(紫外线)
        url_indices = f"https://devapi.qweather.com/v7/indices/1d?location={LOCATION_ID}&key={QWEATHER_KEY}&type=1,3,5"
        resp_indices = requests.get(url_indices).json()

        # 检查数据是否获取成功 (code 200 表示成功)
        if resp_now['code'] != '200' or resp_daily['code'] != '200':
            print(f"❌ API 返回错误: {resp_now.get('code')}")
            return None

        # --- 解析数据 ---
        now = resp_now['now']
        daily = resp_daily['daily'][0] # 今天的预报
        indices = resp_indices['daily'] # 生活指数列表

        # 提取生活指数 (和风返回的是列表，需要遍历查找)
        # 默认值
        suggestion_cloth = "N/A"
        suggestion_uv = "N/A"
        suggestion_sport = "N/A"
        
        for item in indices:
            if item['type'] == '3': # 穿衣
                suggestion_cloth = item['text']
            elif item['type'] == '5': # 紫外线
                suggestion_uv = item['category']
            elif item['type'] == '1': # 运动
                suggestion_sport = item['text']

        # --- 组装漂亮的 HTML ---
        html_content = f"""
        <div style="font-family: '微软雅黑', sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 24px;">📅 成都天气日报</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{daily['fxDate']} (今天)</p>
            </div>

            <div style="padding: 25px;">
                <div style="text-align: center; margin-bottom: 25px;">
                    <span style="font-size: 48px; font-weight: bold; color: #333;">{now['temp']}°</span>
                    <span style="font-size: 20px; color: #666; margin-left: 10px;">{now['text']}</span>
                </div>

                <div style="display: flex; justify-content: space-between; background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="text-align: center; flex: 1;">
                        <div style="font-size: 12px; color: #888;">最高/最低</div>
                        <div style="font-weight: bold; color: #333;">{daily['tempMin']}° ~ {daily['tempMax']}°</div>
                    </div>
                    <div style="text-align: center; flex: 1; border-left: 1px solid #ddd;">
                        <div style="font-size: 12px; color: #888;">相对湿度</div>
                        <div style="font-weight: bold; color: #333;">{now['humidity']}%</div>
                    </div>
                    <div style="text-align: center; flex: 1; border-left: 1px solid #ddd;">
                        <div style="font-size: 12px; color: #888;">风向风力</div>
                        <div style="font-weight: bold; color: #333;">{now['windDir']} {now['windScale']}级</div>
                    </div>
                </div>

                <h3 style="font-size: 16px; border-left: 4px solid #764ba2; padding-left: 10px; margin-bottom: 15px;">💡 生活指数</h3>
                
                <div style="margin-bottom: 10px;">
                    <strong style="color: #555;">👕 穿衣建议：</strong>
                    <span style="color: #333; line-height: 1.6;">{suggestion_cloth}</span>
                </div>
                <div style="margin-bottom: 10px;">
                    <strong style="color: #555;">☀️ 紫外线：</strong>
                    <span style="color: #333;">{suggestion_uv}</span>
                </div>
                 <div style="margin-bottom: 10px;">
                    <strong style="color: #555;">🏃 运动建议：</strong>
                    <span style="color: #333;">{suggestion_sport}</span>
                </div>
                
                 <div style="margin-top: 20px; font-size: 13px; color: #888; text-align: center; border-top: 1px dashed #eee; padding-top: 10px;">
                    🌅 日出 {daily['sunrise']} | 🌇 日落 {daily['sunset']}
                </div>
            </div>

            <div style="background-color: #f0f2f5; padding: 10px; text-align: center; font-size: 12px; color: #999;">
                数据来源：和风天气 API | GitHub Actions 自动推送
            </div>
        </div>
        """
        return html_content

    except Exception as e:
        print(f"❌ API 请求或解析出错: {e}")
        return None

def send_email(content):
    # ... (这部分代码完全不用变，保留原来的即可) ...
    # 为了完整性，请确保保留之前的 send_email 函数代码
    # 如果你懒得翻，下面是简写版（请确保和之前的一样）：
    print("🚀 正在连接 QQ 邮箱服务器...")
    if not MAIL_USER or not MAIL_PASS:
        print("❌ 错误：未找到邮箱账号或密码")
        return
    
    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = formataddr(("天气小助手", MAIL_USER))
    msg['To'] = ",".join(RECEIVERS)
    msg['Subject'] = Header('早安！今日天气详报 ☀️', 'utf-8')

    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(MAIL_USER, MAIL_PASS)
        server.sendmail(MAIL_USER, RECEIVERS, msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    weather_html = get_weather_data()
    if weather_html:
        send_email(weather_html)
