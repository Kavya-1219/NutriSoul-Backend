import smtplib
import ssl

def test_gmail_smtp_465():
    host = "smtp.gmail.com"
    port = 465
    user = "nutrisoulapp@gmail.com"
    password = "pfpu konq fxyy gdoo"

    print(f"Connecting to {host}:{port} (SSL)...")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context, timeout=10) as server:
            print("Connected! Logging in...")
            server.login(user, password)
            print("Login successful!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gmail_smtp_465()
