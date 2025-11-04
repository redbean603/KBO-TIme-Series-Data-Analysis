from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import time

# chrome option
options = Options()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

# url
url = "https://www.koreabaseball.com/Record/Crowd/GraphDaily.aspx"
driver.get(url)
time.sleep(2)

def data_process(url, year):


    # choose year button
    select = Select(driver.find_element(By.ID, "cphContents_cphContents_cphContents_ddlSeason"))
    select.select_by_value(str(year))
    time.sleep(1)

    # click 'search' button
    search_btn = driver.find_element(By.ID, "cphContents_cphContents_cphContents_btnSearch")
    search_btn.click()

    # wait until the page get renewed
    time.sleep(3)

    # Table HTML parsing
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table", {"class": "tData"})
    rows = table.find("tbody").find_all("tr")

    data = []
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) == 6:  
            data.append(cols)

    columns = ["date", "day", "Home", "Away", "place", "crowds"]
    df = pd.DataFrame(data, columns=columns)
    df["crowds"] = df["crowds"].str.replace(",", "").astype(int)
    df["date"] = pd.to_datetime(df["date"], format="%Y/%m/%d")

    print(df.head(), "\n")
    print(f"number of data from {year}:", len(df))

    return df

df_2025 = data_process(url, 2025)
df_2024 = data_process(url, 2024)
df_2023 = data_process(url, 2023)

# download into csv file option
df_2025.to_csv("kbo_crowd_2025.csv", index=False, encoding="utf-8-sig")
df_2024.to_csv("kbo_crowd_2024.csv", index=False, encoding="utf-8-sig")
df_2023.to_csv("kbo_crowd_2023.csv", index=False, encoding="utf-8-sig")


driver.quit()