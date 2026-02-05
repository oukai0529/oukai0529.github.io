import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ================= 配置区域 (QQ邮箱版) =================
# 从环境变量读取账号密码
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")

# ⚠️ 在这里修改你想发给谁（可以写多个，用逗号隔开）
# 比如：["你的号@qq.com", "女朋友@qq.com", "室友@163.com"]
RECEIVERS = ["你的号@qq.com"] 
# =======================================================

def get_weather():
    """
    爬虫函数：抓取成都天气 (逻辑不变)
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
        
        # 处理温度可能不存在的情况
        if today_node.find('span'):
            high_temp = today_node.find('span').text
        else:
            high_temp = "N/A"
            
        low_temp = today_node.find('i').text
        wind = today_node.find('p', class_='win').find('i').text

        # 组装成 HTML 格式，这样邮件里也是彩色的
        html_content = f"""
        <div style="font-family: '微软雅黑', sans-serif; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #eee; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #0099FF; padding: 20px; text-align: center; color: white;">
                <h2 style="margin: 0;">📅 成都天气日报</h2>
                <p style="margin: 5px 0 0 0;">{date}</p>
            </div>
            <div style="padding: 20px;">
                <p style="font-size: 16px;"><strong>🌍 城市：</strong>成都 (UESTC)</p>
                <p style="font-size: 16px;"><strong>🌤️ 天气：</strong><span style="color: #FF9900; font-weight: bold;">{weather}</span></p>
                <p style="font-size: 16px;"><strong>🌡️ 温度：</strong><span style="color: #0066CC;">{low_temp}</span> ~ <span style="color: #CC0000;">{high_temp}</span></p>
                <p style="font-size: 16px;"><strong>🌬️ 风力：</strong>{wind}</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #999;">
                来自 GitHub Actions 自动播报
            </div>
        </div>
        """
        return html_content

    except Exception as e:
        print(f"❌ 爬虫出错了: {e}")
        return None

def send_email(content):
    """
    使用 SMTP 发送邮件
    """
    print("🚀 正在连接 QQ 邮箱服务器...")
    
    if not MAIL_USER or not MAIL_PASS:
        print("❌ 错误：未找到邮箱账号或密码，请检查 GitHub Secrets！")
        return

    # 邮件内容设置
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header(f"天气助手 <{MAIL_USER}>", 'utf-8')
    message['To'] = Header(",".join(RECEIVERS), 'utf-8')
    message['Subject'] = Header('早安！今日天气提醒 ☀️', 'utf-8')

    try:
        # 连接 QQ 邮箱 SMTP 服务器 (端口 465, 使用 SSL 安全连接)
        smtp_obj = smtplib.SMTP_SSL('smtp.qq.com', 465) 
        # 登录
        smtp_obj.login(MAIL_USER, MAIL_PASS)
        # 发送
        smtp_obj.sendmail(MAIL_USER, RECEIVERS, message.as_string())
        smtp_obj.quit()
        print("✅ 邮件发送成功！")
    except smtplib.SMTPException as e:
        print(f"❌ 邮件发送失败: {e}")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

if __name__ == "__main__":
    weather_info = get_weather()
    if weather_info:
        send_email(weather_info)
    else:
        print("没爬到数据")
