def send_email(content):
    import smtplib
    import ssl
    import traceback
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from datetime import datetime

    try:
        # ========= 参数安全检查 =========
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            print("❌ 未读取到邮箱账号或密码，请检查 GitHub Secrets")
            return False

        sender = SENDER_EMAIL.strip()
        password = SENDER_PASSWORD.strip()
        receiver = RECEIVER_EMAIL.strip()

        # ========= 构建邮件 =========
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = f"💻 每日 IT 与硬件前沿速递 - {datetime.now().strftime('%Y-%m-%d')}"

        msg.attach(MIMEText(content, "html", "utf-8"))

        print(f"📡 正在连接 SMTP 服务器: {SMTP_SERVER}:587")

        # ========= 建立SMTP连接 =========
        server = smtplib.SMTP(
            host=SMTP_SERVER,
            port=587,
            timeout=30
        )

        # GitHub Actions 调试日志
        server.set_debuglevel(1)

        # ========= SMTP握手 =========
        server.ehlo()

        print("🔐 启动 STARTTLS 加密...")
        server.starttls()   # ⚠️ 不使用 create_default_context（避免 Runner TLS 兼容问题）

        server.ehlo()

        # ========= 连接存活测试 =========
        code, msg_resp = server.noop()
        print("SMTP连接状态:", code, msg_resp)

        # ========= 登录 =========
        print(f"🔑 登录邮箱: {sender}")
        server.login(sender, password)

        print("✅ 登录成功，开始发送邮件...")

        # ========= 发送 =========
        server.send_message(msg)

        # ========= 关闭 =========
        server.quit()

        print("🎉 邮件发送成功！")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP认证失败：请确认使用【邮箱应用专用密码】")

    except smtplib.SMTPServerDisconnected:
        print("❌ SMTP服务器主动断开连接（常见于密码或TLS问题）")

    except smtplib.SMTPConnectError:
        print("❌ SMTP连接失败，服务器拒绝访问")

    except TimeoutError:
        print("❌ 连接超时，可能被网络限制")

    except Exception:
        print("\n❌ 邮件发送失败，完整错误如下：")
        traceback.print_exc()

    return False
