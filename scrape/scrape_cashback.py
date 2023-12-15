import requests
from bs4 import BeautifulSoup
from scrape_cashback_table import scrape_individual
import openai
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

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
    card_info = scrape_individual(link)
    print(card_info)
