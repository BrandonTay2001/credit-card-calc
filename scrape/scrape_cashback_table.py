import requests
from bs4 import BeautifulSoup

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

            # add to lists
            categoryList.append(category)
            cashbackPercentageList.append(cashback_percentage)
            monthlyCapList.append(monthly_cap)
            spendList.append(spend)
    
    # need to call GPT to split categorize the categoryList, ie. we want to split 'Dining, Entertainment' into ['Dining', 'Entertainment']
    # also need to call GPT to convert text like 'from RM1500 or above' to range of numbers [1500, float('inf')]
    
    return [categoryList, cashbackPercentageList, monthlyCapList, spendList]