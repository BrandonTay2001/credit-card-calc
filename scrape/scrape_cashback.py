import requests
from bs4 import BeautifulSoup
from scrape_cashback_table import scrape_individual
import openai
import pymongo
import os
from dotenv import load_dotenv

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
db = client["cardCalc"]
col = db["cashback"]

url = "https://ringgitplus.com/en/credit-card/cashback/"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

ul_tag = soup.find("ul", class_="Products CRCD")
li_tags = ul_tag.find_all("li")

links_and_names = {}

for li in li_tags:
    a_tag = li.find("a")
    link = "https://ringgitplus.com" + a_tag["href"]
    name = a_tag.text
    links_and_names[name] = link
    rows = scrape_individual(link)
    
    seen = set()
    
    # if name is not in db, add it
    if col.find_one({"name": name}) == None:
        col.insert_one({"name": name, "link": link, "categories": {}})

    categories = {}

    for row in rows:
        # seen key: (categories, spend)
        if (tuple(row[0]), row[3]) in seen:
            continue
        seen.add((row[0], row[3]))
        
        if tuple(row[0]) in categories:
            categories[tuple(row[0])].append({"cashback_percentage": row[1], "monthly_cap": row[2], "spend": row[3]})
        else:
            categories[tuple(row[0])] = [{"cashback_percentage": row[1], "monthly_cap": row[2], "spend": row[3]}]
        
    col.update_one({"name": name}, {"$set": {"categories": categories}})