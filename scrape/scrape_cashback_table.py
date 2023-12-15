import requests
from bs4 import BeautifulSoup
import tinydb
import re

db = tinydb.TinyDB('category_mapping.json')
mapping = db.all()

def transform_text(text):
    lower_bound = 0 # Default lower bound
    upper_bound = float('inf')  # Default upper bound

    # Extract lower bound
    match = re.search(r'from RM([\d,]+)', text)
    if match:
        lower_bound = int(match.group(1).replace(',', ''))

    # Extract upper bound
    match = re.search(r'up to RM([\d,]+)', text)
    if match:
        upper_bound = int(match.group(1).replace(',', ''))

    # Extract upper bound for "from RM500 or above monthly"
    match = re.search(r'from RM([\d,]+) or above', text)
    if match:
        upper_bound = float('inf')

    return [lower_bound, upper_bound]

def scrape_individual(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    table_wrapper = soup.find_all("div", class_="table-wrapper")[0]
    tbody = table_wrapper.find("tbody")
    tr_tags = tbody.find_all("tr")

    categoryList = []
    cashbackPercentageList = []
    monthlyCapList = []
    spendList = []

    for tr in tr_tags:
        for tr in tr_tags:
            category = tr.find("td").text
            cashback_percentage = tr.find("td").find_next("td").text
            monthly_cap = tr.find("td").find_next("td").find_next("td").text
            spend = tr.find("td").find_next("td").find_next("td").find_next("td").text

            entryCategories = []

            # loop through mapping and add value to categoryList
            for key in mapping[0]:
                if key in category.lower() and mapping[0][key] != None:
                    if mapping[0][key] == 'Others' and 'overseas' in category.lower():
                        continue
                    entryCategories.append(mapping[0][key])

            # clean the cashback_percentage
            cashback_percentage = float(cashback_percentage.replace('%', ''))

            # clean the monthly_cap
            if 'RM' in monthly_cap:
                monthly_cap = float(monthly_cap.replace('RM', ''))
            else:   # no cap
                monthly_cap = float('inf')

            # clean the spend
            spend = transform_text(spend)

            # add to lists
            categoryList.append(entryCategories)
            cashbackPercentageList.append(cashback_percentage)
            monthlyCapList.append(monthly_cap)
            spendList.append(spend)

    return [categoryList, cashbackPercentageList, monthlyCapList, spendList]

