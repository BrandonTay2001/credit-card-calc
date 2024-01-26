import requests
from bs4 import BeautifulSoup
import tinydb
import re
import pymongo
from dotenv import load_dotenv

from dotenv import load_dotenv, find_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

client = pymongo.MongoClient(f"mongodb+srv://{DB_USER}:{DB_PASS}@hentaicluster.hcelnlh.mongodb.net/?retryWrites=true&w=majority")
db = client["cardCalc"]
colImg = db["cashbackImg"]

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

    tableList = []

    for i, tr in enumerate(tr_tags):
        
        category = tr.find("td").text
        cashback_percentage = tr.find("td").find_next("td").text
        monthly_cap = tr.find("td").find_next("td").find_next("td").text
        spend = tr.find("td").find_next("td").find_next("td").find_next("td").text

        entryCategories = []

        # remove punctuations from category
        category = re.sub(r'[^\w\s]', ' ', category)
        categoryTextArray = category.lower().split()

        # loop through mapping and add value to categoryList
        for key in mapping[0]:
            if key in categoryTextArray and mapping[0][key] != None:
                if mapping[0][key] == 'Others' and 'overseas' in categoryTextArray:
                    continue
                if mapping[0][key] in entryCategories:
                    continue
                entryCategories.append(mapping[0][key])
        if 'Others' in entryCategories and ('exclude' in categoryTextArray or 'excludes' in categoryTextArray): # edge case 1 - exclude others
            entryCategories = ['Others']
        if not entryCategories: # edge case 2 - no categories
            entryCategories.append('Others')

        # clean the cashback_percentage
        cashback_percentage = float(cashback_percentage.replace('%', ''))

        # remove comma from monthly_cap
        monthly_cap = monthly_cap.replace(',', '')

        # clean the monthly_cap
        if 'RM' in monthly_cap:
            monthly_cap = float(monthly_cap.replace('RM', ''))
        else:   # no cap
            monthly_cap = float('inf')

        # clean the spend
        spend = transform_text(spend)

        # add to list
        tableList.append([entryCategories, cashback_percentage, monthly_cap, spend])

    return tableList

def construct_table(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    table_wrapper = soup.find_all("div", class_="table-wrapper")[0]
    tbody = table_wrapper.find("tbody")
    tr_tags = tbody.find_all("tr")

    tableList = []

    for i, tr in enumerate(tr_tags):
        
        category = tr.find("td").text
        cashback_percentage = tr.find("td").find_next("td").text
        monthly_cap = tr.find("td").find_next("td").find_next("td").text
        spend = tr.find("td").find_next("td").find_next("td").find_next("td").text
        
        # remove comma from monthly_cap
        monthly_cap = monthly_cap.replace(',', '')
    
        # clean the spend
        spend = transform_text(spend)

        spendText = f"RM{spend[0]} - RM{spend[1]}"
        
        # Construct HTML table
        tableList.append(f"<tr><td>{category}</td><td>{cashback_percentage}</td><td>{monthly_cap}</td><td>{spendText}</td></tr>")
    
    # Join the table rows
    table_html = "<table><tr><th>Category</th><th>Cashback</th><th>Monthly Cap</th><th>When Spending Within</th></tr>"
    table_html += "".join(tableList)
    table_html += "</table>"
    
    return table_html

def scrape_img(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    header = soup.find('header', class_='Hero product')
    img_tag = header.find('img')
    img_src = img_tag['src']
    return img_src

print(construct_table("https://ringgitplus.com/en/credit-card/UOB-ONE-Card.html?filter=UOB"))