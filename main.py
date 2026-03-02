import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pytz
import os
import ssl
from bs4 import BeautifulSoup

# 1. 配置区：你想采集的IT与硬件网站RSS源
RSS_FEEDS = {
    # --- 新增：硬件与操作系统发售资讯 ---
    "IT之家 (硬件与系统资讯)": "https://www.ithome.com/rss/",
    "少数派 (软硬件与系统体验)": "https://sspai.com/feed",
    "Solidot (开源系统与极客硬件)": "https://www.solidot.org/index.rss",
    "Tom's Hardware (全球PC硬件/英文)": "https://www.tomshardware.com/feeds/all",
    "MacRumors (苹果系统与设备/英文)": "https://feeds.macrumors.com/MacRumors-All",

    # --- 原有：开发与IT技术 ---
    "V2EX 最热主题": "https://www.v2ex.com/index.xml",
    "掘金前端": "https://juejin.cn/rss?sort=three_days_newest",
    "博客园": "https://feed.cnblogs.com/blog/sitehome/rss",
    "InfoQ 架构": "https://www.infoq.cn/feed"
}
import os
import requests
from datetime import datetime

# ===== Resend 配置 =====
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

import os
import requests
from datetime import datetime

# ===== Resend 配置 =====
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def send_email(content):
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY 未读取到")
        return
    if not RECEIVER_EMAIL:
        print("❌ RECEIVER_EMAIL 未读取到")
        return

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "Daily News <zhouyulv@Gmail.com>",  # 必须是注册邮箱
        "to": [RECEIVER_EMAIL],
        "subject": f"每日 IT 与硬件前沿速递 - {datetime.now().strftime('%Y-%m-%d')}",
        "html": content
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        print("HTTP状态码:", response.status_code)
        print("返回内容:", response.text)
        response.raise_for_status()
        print("🎉 邮件发送成功")
    except requests.exceptions.ConnectionError:
        print("❌ 网络连接异常")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print("❌ 未知错误:", e)


