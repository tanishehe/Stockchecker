from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

email = 'put your email here'
email2 = 'put another email here'
email2password = 'put email2 password here'

def send_email_notification(to_email, subject, body):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.environ.get('EMAIL_USER', email2)
        sender_password = os.environ.get('EMAIL_PASSWORD', email2password)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()

        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def check_sold_out_status(url):
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        print(f"Loading: {url}")
        driver.get(url)

        time.sleep(3)

        try:
            pincode_selectors = [
                "input[name*='pincode']",
                "input[name*='zip']",
                "input[name*='postal']",
                "input[id*='pincode']",
                "input[id*='zip']",
                "input[id*='postal']",
                "input[placeholder*='pincode']",
                "input[placeholder*='Pincode']",
                "input[placeholder*='PINCODE']",
                "input[placeholder*='zip']",
                "input[placeholder*='Zip']",
                "input[placeholder*='postal']",
                "input[placeholder*='Postal']"
            ]

            pincode_input = None
            for selector in pincode_selectors:
                try:
                    pincode_input = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue

            if pincode_input:
                pincode_input.clear()
                pincode_input.send_keys("110030")

                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button[id*='submit']",
                    "button[class*='submit']",
                    ".pincode-submit",
                    "[onclick*='pincode']"
                ]

                submit_clicked = False
                for submit_selector in submit_selectors:
                    try:
                        submit_button = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector))
                        )
                        submit_button.click()
                        submit_clicked = True
                        break
                    except:
                        continue

                if not submit_clicked:
                    from selenium.webdriver.common.keys import Keys
                    pincode_input.send_keys(Keys.RETURN)

                time.sleep(3)

        except Exception as e:
            pass

        try:
            alert_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
            )

            alert_text = alert_div.text.strip()

            is_sold_out = 'sold out' in alert_text.lower()

            return {
                'found_alert': True,
                'alert_text': alert_text,
                'is_sold_out': is_sold_out,
                'status': 'Sold Out' if is_sold_out else 'Available'
            }

        except TimeoutException:
            return {
                'found_alert': False,
                'alert_text': None,
                'is_sold_out': False,
                'status': 'Available'
            }

    except WebDriverException as e:
        return {
            'error': f'WebDriver error: {e}',
            'found_alert': False,
            'is_sold_out': False
        }
    except Exception as e:
        return {
            'error': f'Unexpected error: {e}',
            'found_alert': False,
            'is_sold_out': False
        }
def test_email_setup():
    """Test email configuration before enabling notifications"""
    test_subject = "Test Email - Amul Stock Checker"
    test_body = "This is a test email to verify your email setup is working.\n\nIf you received this, your email configuration is correct!"

    print("Testing email configuration...")
    success = send_email_notification(notification_email, test_subject, test_body)

    if success:
        print("✅ Email test successful! You can now enable notifications.")
        return True
    else:
        print("❌ Email test failed. Please check your email setup.")
        return False

def check_multiple_products():
    """Check all products and return summary - callable from web endpoints"""
    urls_to_check = [
        "https://shop.amul.com/en/product/amul-whey-protein-32-g-or-pack-of-60-sachets",
        "https://shop.amul.com/en/product/amul-whey-protein-32-g-or-pack-of-30-sachets",
        "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-30-sachets",
        "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-60-sachets"
    ]

    notification_email = os.environ.get('NOTIFICATION_EMAIL', email) #PUT YOUR EMAIL HERE
    enable_email_notifications = True

    print(f"Checking {len(urls_to_check)} products...")

    available_products = []
    sold_out_products = []

    for url in urls_to_check:
        print(f"\nChecking: {url}")
        result = check_sold_out_status(url)

        status = result.get('status', 'Unknown')
        print(f"Status: {status}")

        if status == 'Available':
            available_products.append(url)
        elif status == 'Sold Out':
            sold_out_products.append(url)

        if 'error' in result:
            print(f"Error: {result['error']}")

    summary = f"Available: {len(available_products)}, Sold out: {len(sold_out_products)}"

    # Send email notification if any products are available
    if available_products and enable_email_notifications:
        subject = f"🚨 Products Available - {len(available_products)} items in stock!"
        body = "Freaking finally the following products are now AVAILABLE:\n\n"
        for url in available_products:
            body += f"✅ {url}\n"
        body += f"\n\nChecked on: {time.strftime('%Y-%m-%d %H:%M:%S')}"

        if send_email_notification(notification_email, subject, body):
            print("Email notification sent successfully!")
            summary += " | Email sent"
        else:
            print("Failed to send email notification")
            summary += " | Email failed"
    elif available_products and not enable_email_notifications:
        print("Email notifications are disabled")
        summary += " | Email disabled"
    else:
        print("No products are currently available")
        summary += " | No availability"

    return {
        'available_count': len(available_products),
        'sold_out_count': len(sold_out_products),
        'available_products': available_products,
        'sold_out_products': sold_out_products,
        'summary': summary
    }

if __name__ == "__main__":
    '''urls_to_check = [
        "https://shop.amul.com/en/product/amul-whey-protein-32-g-or-pack-of-60-sachets",
        "https://shop.amul.com/en/product/amul-whey-protein-32-g-or-pack-of-30-sachets",
        "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-30-sachets",
        "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-60-sachets"
    ]'''
    urls_to_check = [
        "https://shop.amul.com/en/product/amul-kool-protein-milkshake-or-arabica-coffee-180-ml-or-pack-of-8"
    ]

    notification_email = os.environ.get('NOTIFICATION_EMAIL', email)  # Replace with your email address
    enable_email_notifications = True  # Set to True after setting up email credentials
    test_email_mode = False  # Set to True to test email setup first

    if test_email_mode:
        print("Running email test...")
        if test_email_setup():
            print("You can now set test_email_mode = False and enable_email_notifications = True")
        else:
            print("Please fix email setup before enabling notifications")
        exit(0)

    print(f"Checking {len(urls_to_check)} products...")

    available_products = []
    sold_out_products = []

    for url in urls_to_check:
        print(f"\nChecking: {url}")
        result = check_sold_out_status(url)

        status = result.get('status', 'Unknown')
        print(f"Status: {status}")

        if status == 'Available':
            available_products.append(url)
        elif status == 'Sold Out':
            sold_out_products.append(url)

        if 'error' in result:
            print(f"Error: {result['error']}")

    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"Available products: {len(available_products)}")
    print(f"Sold out products: {len(sold_out_products)}")
    print(f"{'='*50}")

    if available_products and enable_email_notifications:
        subject = f"Products Available - {len(available_products)} items in stock"
        body = "Great news! The following products are now AVAILABLE:\n\n"
        for url in available_products:
            body += f"✅ {url}\n"
        body += "\n⏰ Check them out quickly before they're gone!"
        body += f"\n\nChecked on: {time.strftime('%Y-%m-%d %H:%M:%S')}"

        if send_email_notification(notification_email, subject, body):
            print("✅ Email notification sent successfully!")
        else:
            print("❌ Failed to send email notification")
    elif available_products and not enable_email_notifications:
        print("📧 Email notifications are disabled. Enable them by setting enable_email_notifications = True")
        print("📧 Make sure to set up your Gmail app password first!")
    else:
        print("📦 No products are currently available. Will check again next time.")