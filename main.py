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

# 2. 邮箱配置 (Gmail)
SMTP_SERVER = "smtp.gmail.com"  
SMTP_PORT = 465                 
SENDER_EMAIL = os.environ.get("SMTP_USER")     
SENDER_PASSWORD = os.environ.get("SMTP_PASS")  
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL") 

def clean_html_to_text(html_content):
    """把网页源代码清洗成纯粹的文字，去掉所有链接、图片和标签"""
    if not html_content:
        return ""
    # 使用 BeautifulSoup 解析并提取纯文本
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    
    # 如果正文太长，截取前 150 个字
    if len(text) > 150:
        text = text[:150] + "..."
    return text

def get_latest_news():
    """获取新闻标题和正文纯文本"""
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    yesterday = now - timedelta(days=1)
    
    html_content = "<h2 style='text-align:center; color:#2c3e50;'>每日 IT 与硬件资讯精选 (纯净版)</h2>"
    
    for site_name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            html_content += f"<h3 style='background-color:#f0f2f5; padding:8px; border-left:4px solid #3498db;'>[{site_name}]</h3><ul style='list-style-type:none; padding-left:0;'>"
            
            count = 0
            for entry in feed.entries:
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_time = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(tz)
                    
                    # 只提取过去 24 小时内发布的消息
                    if pub_time > yesterday:
                        # 提取文章的正文/摘要
                        article_text = ""
                        if hasattr(entry, 'summary'):
                            article_text = clean_html_to_text(entry.summary)
                        elif hasattr(entry, 'description'):
                            article_text = clean_html_to_text(entry.description)
                            
                        # 排版：标题加粗，正文灰色缩小，绝对不含超链接
                        html_content += f"<li style='margin-bottom: 20px; border-bottom: 1px dashed #e0e0e0; padding-bottom: 10px;'>"
                        html_content += f"<div style='margin-bottom: 5px;'><strong style='color:#222; font-size:16px;'>{entry.title}</strong> <span style='color:#999; font-size:12px;'>({pub_time.strftime('%H:%M')})</span></div>"
                        
                        # 如果有正文，则显示正文
                        if article_text:
                            html_content += f"<div style='color:#666; font-size:14px; line-height:1.6;'>{article_text}</div>"
                        else:
                            html_content += f"<div style='color:#ccc; font-size:12px;'>(无正文内容)</div>"
                            
                        html_content += "</li>"
                        count += 1
                        
                # 考虑到带正文比较长，每个网站最多取 5 篇，防止邮件过长
                if count >= 5:
                    break
                    
            if count == 0:
                html_content += "<li style='color:#999;'>今日暂无最新发售或资讯更新</li>"
            html_content += "</ul>"
            
        except Exception as e:
            html_content += f"<p style='color:red;'>抓取 {site_name} 失败: {str(e)}</p>"
            
    return html_content

def send_email(content):
    import smtplib
    import ssl
    import traceback
    
    # 1. 账号密码读取检查（防止 Secrets 没配置好）
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ 严重错误：读取不到邮箱或密码！请检查 GitHub Secrets 中的 SMTP_USER 和 SMTP_PASS 是否配置正确。")
        return
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"💻 每日 IT 与硬件前沿速递 - {datetime.now().strftime('%Y-%m-%d')}"
    msg.attach(MIMEText(content, 'html', 'utf-8'))
    
    try:
        print(f"正在尝试连接 {SMTP_SERVER} 的 587 端口...")
        # 2. 改用 587 端口 + STARTTLS 加密 (Gmail 官方推荐的另一种稳定方式)
        server = smtplib.SMTP(SMTP_SERVER, 587, timeout=15)
        server.set_debuglevel(1)  # 强制开启超级详细的底层网络日志
        
        server.ehlo()
        server.starttls(context=ssl.create_default_context()) # 启动安全加密传输
        server.ehlo()
        
        print(f"服务器连接成功，准备登录账号: {SENDER_EMAIL} ...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        print("登录成功！正在发送邮件...")
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("🎉 邮件发送成功！请查收。")
        
    except Exception as e:
        print("\n❌ 邮件发送失败！详细诊断日志如下：")
        traceback.print_exc() # 打印红色的详细报错追踪代码
    print("开始抓取新闻与正文...")
    news_content = get_latest_news()
    print("开始发送邮件...")
    send_email(news_content)

