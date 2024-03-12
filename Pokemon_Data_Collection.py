from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.mouse_button import MouseButton
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def getLimitless(url):
    site = requests.get(url)
    soup = BeautifulSoup(site.content, "html.parser")
    table = soup.find('table')

    # Initialize a list to store the extracted data
    table_data = []

    # Iterate over the rows in the table
    for row in table.find_all('tr'):
        # Extract the text from each cell in the row
        row_data = [cell.text for cell in row.find_all('td')]
        span = row.find('span', attrs={'data-tooltip': True})
        tooltip = ''
        if span:
            # Extract the value of the data-tooltip attribute
            tooltip = span['data-tooltip']
            # Append the tooltip to the table_data list
        # Append the row data to the table_data list
        if tooltip:
            table_data.append([row_data, tooltip])
        else:
            table_data.append([row_data, ''])

    #Cleaning the data
    deck_list = []
    names = []
    for row in table_data:
        if row[0]:
            deck_list.append(row[1])
            names.append(row[0][1].strip().lower())

    #Making dictionary to lookup data
    lookup_dict = {"Name": names, "Deck": deck_list}
    return lookup_dict

def getRK9(url):
    options = webdriver.FirefoxOptions()
    options.page_load_strategy = 'normal'
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    rounds = 18
    dict = {}
    tables = [0, 200, 200, 200, 200, 200, 200, 200, 200, 200, 50, 50, 50, 50, 50, 50, 4, 2, 1]
    for round_num in range (10, rounds+1):
        driver.find_element(By.ID, "P2R"+str(round_num)+"-tab").click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='P2R"+str(round_num)+"']/div["+str(tables[round_num])+"]")))
        table = driver.find_element(By.XPATH, "//*[@id='P2R"+str(round_num)+"']")
        rows = table.find_elements(By.TAG_NAME, "div")
        data = []
        for row in rows:
            data.append(row.text)
        dict["Round " + str(round_num)] = [data]
    driver.quit()
    return pd.DataFrame(dict)

name = input("name of tourney:")
frame = getRK9(input("RK9 pairings link:"))
frame.to_csv('Dirty Pokemon Data_'+name+'.csv')

df = pd.DataFrame(getLimitless(input("Limitless standings link")))
df.to_csv('Cross-Reference Sheet_'+name+'.csv')

