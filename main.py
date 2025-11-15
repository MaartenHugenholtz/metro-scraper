from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import time

app = FastAPI(title="Metro Departures API")

# Regex pattern for scraping
pattern = re.compile(
    r"(?P<time>\d{2}:\d{2})"  # HH:MM
    r"(?P<line>[A-Z])"  # Line letter
    r"(?P<destination>.+?)"  # Destination
    r"RET Metro"  # Fixed text
    r"Perron (?P<platform>\d+)"  # Platform number
)

# ----------------------------------------------------------
# 🧠 GLOBAL, REUSED FIREFOX INSTANCE  (BIG MEMORY SAVING)
# ----------------------------------------------------------


def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=300,300")
    options.add_argument("--js-flags=--lite-mode")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-features=ScriptStreaming")

    profile = webdriver.FirefoxProfile()

    # Disable images
    profile.set_preference("permissions.default.image", 2)

    # Disable caches
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)

    # Minimal rendering
    profile.set_preference("layout.css.devPixelsPerPx", "0.1")

    # Disable plugins + media
    profile.set_preference("dom.ipc.plugins.enabled", False)
    profile.set_preference("media.autoplay.default", 1)

    # Start browser
    options.profile = profile
    driver = webdriver.Firefox(options=options)

    # Implicit wait once (not inside function)
    driver.implicitly_wait(10)

    return driver


# Create a global, persistent browser
driver = create_driver()


# ----------------------------------------------------------
# SCRAPER FUNCTION (reuses browser)
# ----------------------------------------------------------
def scrape_departures():
    url = "https://9292.nl/locaties/schiedam_metrostation-parkweg/departures"

    # Load the page
    driver.get(url)

    # Wait briefly for JavaScript-rendered elements
    time.sleep(1)

    # Extract then immediately release page content
    html = driver.page_source

    # Parse outside of Selenium (frees DOM memory)
    soup = BeautifulSoup(html, "html.parser")

    departures = []
    for block in soup.select("div.bg-08dp"):
        match = pattern.search(block.text)
        if match:
            departures.append(match.groupdict())

    return departures


# ----------------------------------------------------------
# API endpoint
# ----------------------------------------------------------
@app.get("/departures")
def get_departures():
    data = scrape_departures()
    return {"departures": data}
