from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import re
from bs4 import BeautifulSoup

app = FastAPI()

pattern = re.compile(
    r"(?P<time>\d{2}:\d{2})"
    r"(?P<line>[A-Z])"
    r"(?P<destination>.+?)"
    r"RET Metro"
    r"Perron (?P<platform>\d+)"
)


def scrape_departures():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        page = browser.new_page()
        page.goto("https://9292.nl/locaties/schiedam_metrostation-parkweg/departures")

        page.wait_for_timeout(1500)  # allow JS to render

        soup = BeautifulSoup(page.content(), "html.parser")
        browser.close()

        departures = []
        for block in soup.select("div.bg-08dp"):
            match = pattern.search(block.text)
            if match:
                departures.append(match.groupdict())

        return departures


@app.get("/departures")
def get_departures():
    return {"departures": scrape_departures()}
