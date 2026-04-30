import os
import smtplib
from dotenv import load_dotenv

from email.message import EmailMessage
load_dotenv()

def send_email(to_email: str, subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_USER") 
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

    print("=== EMAIL DEBUG INFO ===")
    print(f"SMTP_HOST     : {host}")
    print(f"SMTP_PORT     : {port}")
    print(f"SMTP_USER     : {user}")
    print(f"FROM_EMAIL    : {from_email}")
    print(f"SMTP_USE_TLS  : {use_tls}")
    print(f"Password length : {len(password) if password else 0} characters")

    if not host or not from_email:
        print("❌ Missing SMTP configuration (HOST / USER / PASSWORD)")
        return False

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        print(f"🔄 Connecting to {host}:{port}...")
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            if use_tls:
                smtp.starttls()
            if user and password:
                smtp.login(user, password)
            smtp.send_message(msg)
        return True
    except Exception:
        return False

