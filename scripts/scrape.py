import csv
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

DRIVER_PATH="./scripts/chromedriver.exe"
DELAY=3
service = Service(executable_path=DRIVER_PATH)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

def standardize_hero_name(hero):
    return hero.replace(' ', '-').replace('\'', '').lower()

# Generate list of heroes

driver.get('https://www.dotabuff.com/heroes?show=heroes')
divs = driver.execute_script("""
    return Array.from(document.querySelectorAll('tbody div')).filter(div => 
        !div.id && !div.className
    ).map(div => div.innerText);
""")
heroes = list(set(
    text.strip() for text in divs
    if (len(text.strip()) >= 4 or text == "Axe" or text == "Io") and not any(char.isdigit() for char in text)
))
heroes.sort()
standard_heroes = list(map(standardize_hero_name, heroes))
if os.path.exists("./data/heroes.csv"):
    os.remove("./data/heroes.csv")
with open('./data/heroes.csv', mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # header row
    writer.writerow(['id', "hero", "urlname"])

    id = 0
    for hero in heroes:
        writer.writerow([id, hero, standardize_hero_name(hero)])
        id += 1


# Collect counter data
for hero in standard_heroes:
    counter_path = "./data/counter/{0}.csv".format(hero)
    if os.path.exists(counter_path):
        continue
    driver.get('https://www.dotabuff.com/heroes/{0}/counters'.format(hero))
    counterTable = driver.find_elements(By.CSS_SELECTOR, 'table tbody')[3]
    with open(counter_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # header
        writer.writerow(['hero', 'disadvantage', 'winrate'])
        for table_row in counterTable.find_elements(By.CSS_SELECTOR, 'tr'):
            tds = table_row.find_elements(By.CSS_SELECTOR, 'td')
            writer.writerow([standardize_hero_name(tds[1].text), tds[2].text.replace('%', ''), tds[3].text.replace('%', '')])
        writer.writerow([hero, '0', '50']);

driver.quit()
