import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pytz
import os

# 配置区：你想采集的IT网站RSS源
RSS_FEEDS = {
    "V2EX 最热主题": "https://www.v2ex.com/index.xml",
    "掘金前端": "https://juejin.cn/rss?sort=three_days_newest",
    "博客园": "https://feed.cnblogs.com/blog/sitehome/rss",
    "InfoQ 架构": "https://www.infoq.cn/feed",
    "OSChina 最新资讯": "https://www.oschina.net/news/rss",
    "Hacker News (英文)": "https://news.ycombinator.com/rss"
}

# 邮箱配置 (从环境变量获取，保护隐私)
SMTP_SERVER = "smtp.qq.com"  # 如果用163邮箱，改为 smtp.163.com
SMTP_PORT = 465 # SSL端口
SENDER_EMAIL = os.environ.get("SMTP_USER")     # 发件人邮箱
SENDER_PASSWORD = os.environ.get("SMTP_PASS")  # 邮箱授权码
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL") # 收件人邮箱（可以是同一个）

def get_latest_news():
    """获取过去24小时内的新闻"""
    # 设置时区为北京时间
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    yesterday = now - timedelta(days=1)
    
    html_content = "<h2>每日 IT 资讯精选</h2>"
    
    for site_name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            html_content += f"<h3>[{site_name}]</h3><ul>"
            
            count = 0
            for entry in feed.entries:
                # 解析文章发布时间
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    # 转换时间格式
                    pub_time = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(tz)
                    
                    # 只筛选最近24小时的文章
                    if pub_time > yesterday:
                        html_content += f"<li><a href='{entry.link}'>{entry.title}</a> <span style='color:gray;font-size:12px;'>({pub_time.strftime('%H:%M')})</span></li>"
                        count += 1
                
                # 每个网站最多提取10条，防止邮件过长
                if count >= 10:
                    break
                    
            if count == 0:
                html_content += "<li>今日暂无更新</li>"
            html_content += "</ul><hr>"
            
        except Exception as e:
            html_content += f"<p>抓取 {site_name} 失败: {str(e)}</p><hr>"
            
    return html_content

def send_email(content):
    """发送 HTML 邮件"""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"🚀 每日 IT 资讯速递 - {datetime.now().strftime('%Y-%m-%d')}"
    
    msg.attach(MIMEText(content, 'html', 'utf-8'))
    
    try:
        # 使用 SSL 连接 SMTP 服务器
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    print("开始抓取新闻...")
    news_content = get_latest_news()
    print("开始发送邮件...")
    send_email(news_content)