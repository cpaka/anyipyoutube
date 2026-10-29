# anyIP + Selenium: open Chrome through an anyIP proxy
#
# Components: Python 3.9 or newer, Google Chrome, plus three packages
#   pip install selenium pproxy python-dotenv
# (Selenium fetches the matching chromedriver)
import json, os, subprocess, sys, time

from dotenv import load_dotenv
from selenium import webdriver

# 1. The endpoint and your settings
# Copy one line from your anyIP profile (List view) into .env:
#   ANYIP_PROXY=portal.anyip.io:1080:user_XXXX,country_us,...:PASSWORD
# The endpoint is always portal.anyip.io, port 1080.
# Every setting (type, country, city, session) is a flag in the username.
load_dotenv("../.env")
host, port, username, password = os.environ["ANYIP_PROXY"].split(":")

# 2. A local forwarder logs in for Chrome
# Chrome under Selenium can't send a proxy password, so pproxy listens
# on your machine and forwards every request to anyIP, logged in.
upstream = f"http://{host}:{port}#{username}:{password}"
forwarder = subprocess.Popen(
    [sys.executable, "-m", "pproxy", "-l", "http://127.0.0.1:8899",
     "-r", upstream], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# 3. Launch Chrome through the forwarder
# The disabled features stop Chrome turning http:// pages into https://.
options = webdriver.ChromeOptions()
options.add_argument("--proxy-server=http://127.0.0.1:8899")
options.add_argument(
    "--disable-features=HttpsUpgrades,HttpsFirstBalancedModeAutoEnable")
driver = webdriver.Chrome(options=options)

# 4. Check it works: IP-API is the checker anyIP uses for locations
fields = "country,regionName,city,isp,mobile,proxy"
try:
    driver.get(f"http://ip-api.com/json/?fields={fields}")
    ip = json.loads(driver.find_element("tag name", "body").text)
    print(f"{ip['city']}, {ip['regionName']}, {ip['country']} | {ip['isp']}")
    print(f"mobile: {ip['mobile']} | proxy: {ip['proxy']}")
finally:
    driver.quit()
    forwarder.terminate()
