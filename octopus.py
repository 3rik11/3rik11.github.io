import time
import requests
from datetime import datetime, timedelta
import pytz
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import os

# GPIO setup for buzzer
BUZZER_PIN = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# OLED setup
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Use larger font (ensure the font file exists)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(FONT_PATH):
    raise FileNotFoundError("Font file not found. Please install DejaVu fonts or adjust the path.")
font = ImageFont.truetype(FONT_PATH, 20)  # Larger size

# Octopus API setup
region_code = 'C'
base_url = f'https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-{region_code}/standard-unit-rates/'

def buzz(duration=10):
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def get_price():
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    uk_tz = pytz.timezone('Europe/London')
    local_now = utc_now.astimezone(uk_tz)
    half_hour = local_now.replace(minute=0 if local_now.minute < 30 else 30, second=0, microsecond=0)

    start_time = half_hour.astimezone(pytz.UTC).isoformat()
    end_time = (half_hour + timedelta(minutes=30)).astimezone(pytz.UTC).isoformat()

    params = {'period_from': start_time, 'period_to': end_time}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['value_inc_vat']
    return None

def display_text(text):
    image = Image.new('1', (device.width, device.height))
    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (device.width - w) // 2
    y = (device.height - h) // 2

    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)  # Clear screen
    draw.text((x, y), text, font=font, fill=255)
    device.display(image)

def check_and_display():
    price = get_price()
    if price is not None:
        price_text = f"{price:.2f}p/kWh"
        display_text(price_text)
        print(f"[INFO] Current Price: {price_text}")
        if price < 0:
            buzz(10)
    else:
        display_text("No data")
        print("[WARN] No pricing data available")

try:
    # Immediate check at startup
    check_and_display()
    last_run = None  # Tracks the last half-hour the code ran

    while True:
        now = datetime.now(pytz.timezone('Europe/London'))
        current_minute = now.minute
        current_half_hour = now.replace(second=0, microsecond=0)

        if current_minute in [0, 30] and current_half_hour != last_run:
            last_run = current_half_hour  # Update last run time
            check_and_display()

        time.sleep(10)  # Check every 10 seconds

except KeyboardInterrupt:
    print("Program interrupted by user")

except Exception as e:
    display_text("Error")
    print(f"[ERROR] {e}")

finally:
    GPIO.cleanup()
