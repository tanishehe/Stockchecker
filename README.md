# Amul Stock Notifier 
A Python script that monitors Amul product pages, checks stock availability, and sends email notifications when items are in stock. Designed to track multiple products efficiently and handle location-specific availability via pincode input.

## Features

- Automatically checks **product availability** on the Amul store
- Handles **pincode input** for location-specific stock
- Can monitor **multiple products at once**
- Sends **email alerts** when products are available
- Runs **headlessly**, no browser popping up

---

## Setup

1. **Clone this repo**

```bash
git clone https://github.com/yourusername/amul-stock-notifier.git
cd amul-stock-notifier
```

Install dependencies

```bash
pip install selenium webdriver-manager
Set environment variables for email (Gmail recommended)
```

Set environment variables for email (Gmail recommended)
```bash
export email2="your_email@gmail.com"
export email2password="your_app_password"
export email="email_to_receive_alerts@gmail.com"
```
You need a Gmail App Password if 2FA is enabled.

## Usage

Edit the urls_to_check list in the script with the products you want to track. Then run:
```bash
python amul_stock_notifier.py
```

### Optional flags in the script:

```bash
enable_email_notifications = True – toggle email alerts

test_email_mode = True – test your email setup before running
```

### Example Output
```bash
Checking: https://shop.amul.com/en/product/amul-whey-protein-32-g-or-pack-of-60-sachets
Status: Available

✅ Email notification sent successfully!
SUMMARY:
Available products: 1
Sold out products: 0
```
