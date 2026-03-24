import smtplib
import ssl

def test_gmail_smtp():
    host = "smtp.gmail.com"
    port = 587
    user = "nutrisoulapp@gmail.com"
    password = "pfpu konq fxyy gdoo" # This is the app password from settings.py

    print(f"Connecting to {host}:{port}...")
    try:
        # Create a secure SSL context
        context = ssl.create_default_context()
        
        # Connect to the server
        server = smtplib.SMTP(host, port, timeout=10)
        print("Connected! Starting TLS...")
        server.starttls(context=context)
        print("TLS started. Logging in...")
        server.login(user, password)
        print("Login successful!")
        server.quit()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gmail_smtp()
