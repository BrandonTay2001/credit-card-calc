import pymongo
import os
import os
from dotenv import load_dotenv
import heapq

from dotenv import load_dotenv, find_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

client = pymongo.MongoClient(f"mongodb+srv://{DB_USER}:{DB_PASS}@hentaicluster.hcelnlh.mongodb.net/?retryWrites=true&w=majority")
db = client["cardCalc"]
col = db["cashback"]
colImg = db["cashbackImg"]

class LimitedHeap:
    def __init__(self, limit):
        self.limit = limit
        self.heap = []

    def push(self, item):
        if item[0] == 0:
            return
        heapq.heappush(self.heap, item)
        if len(self.heap) > self.limit:
            heapq.heappop(self.heap)

    def get_heap(self):
        return self.heap

def get_image(card_name):
    return colImg.find_one({"name": card_name})["img_src"]

def calculate_cashback_for_category(spend_amount, tiers):
    cashback = 0
    for tier in tiers:
        if spend_amount >= tier["spend"][1]:
            cashback += min(tier["monthly_cap"], 
                            tier["cashback_percentage"] / 100 * (tier["spend"][1] - tier["spend"][0]))
        elif spend_amount >= tier["spend"][0] and spend_amount < tier["spend"][1]:
            cashback += min(tier["cashback_percentage"] / 100 * (spend_amount - tier["spend"][0]), 
                            tier["monthly_cap"])
            break
    cashback = round(cashback, 2)  # Round to 2 decimal places
    return cashback

def format_cards(cards):
    formatted_cards = []
    for card in cards:
        card_name = card[1]
        card_cashback = card[0]
        card_image = get_image(card_name)
        formatted_card = {
            "name": card_name,
            "cashback_value": card_cashback,
            "img_src": card_image,
            "link": col.find_one({"name": card_name})["link"]
        }
        formatted_cards.append(formatted_card)
    return formatted_cards

def calculate_cashback(petrolSpending, groceriesSpending, onlineSpending, diningSpending, otherSpending):
    category_to_spend = {
        "Petrol": petrolSpending, "Groceries": groceriesSpending, "Online Shopping": onlineSpending,
        "Dining": diningSpending, "Others": otherSpending
    }
    
    # get all cards in db
    cards = list(col.find({}))
    bestTwoPetrol, bestTwoGroceries, bestTwoOnline, bestTwoDining, bestTwoOther = LimitedHeap(2), LimitedHeap(2), LimitedHeap(2), LimitedHeap(2), LimitedHeap(2)
    card_to_total_cashback = {}
    
    # calculate cashback by category
    for card in cards:  # each card
        for cat_group in card['categories']:    # each category group
            if "Petrol" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Petrol"], cat_group["tier"])
                bestTwoPetrol.push((cat_cashback, card["name"]))
            if "Groceries" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Groceries"], cat_group["tier"])
                bestTwoGroceries.push((cat_cashback, card["name"]))
            if "Online Shopping" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Online Shopping"], cat_group["tier"])
                bestTwoOnline.push((cat_cashback, card["name"]))
            if "Dining" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Dining"], cat_group["tier"])
                bestTwoDining.push((cat_cashback, card["name"]))
            if "Others" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Others"], cat_group["tier"])
                bestTwoOther.push((cat_cashback, card["name"])) 

    # calculate total cashback for each card
    for card in cards:
        total_cashback_per_card = 0
        for cat_group in card['categories']:
            totalSpendThisCategoryGrp = 0
            for individual_cat in cat_group['individual_categories']:
                totalSpendThisCategoryGrp += category_to_spend[individual_cat]
            total_cashback_per_card += calculate_cashback_for_category(totalSpendThisCategoryGrp, cat_group["tier"])
        card_to_total_cashback[card["name"]] = total_cashback_per_card

    # get top 2 cards and cashback for each category
    bestTwoPetrolCards = bestTwoPetrol.get_heap()
    bestTwoGroceriesCards = bestTwoGroceries.get_heap()
    bestTwoOnlineCards = bestTwoOnline.get_heap()
    bestTwoDiningCards = bestTwoDining.get_heap()
    bestTwoOtherCards = bestTwoOther.get_heap()
    # get the top 2 cards overall by sorting card_to_total_cashback dict
    bestTwoOverallCards = heapq.nlargest(2, card_to_total_cashback.items(), key=lambda x: x[1])
    bestTwoOverallCards = [(cashback, name) for name, cashback in bestTwoOverallCards]

    bestTwoPetrolCards = format_cards(bestTwoPetrolCards)
    bestTwoGroceriesCards = format_cards(bestTwoGroceriesCards)
    bestTwoOnlineCards = format_cards(bestTwoOnlineCards)
    bestTwoDiningCards = format_cards(bestTwoDiningCards)
    bestTwoOtherCards = format_cards(bestTwoOtherCards)
    bestTwoOverallCards = format_cards(bestTwoOverallCards)

    return {
        "bestTwoPetrolCards": bestTwoPetrolCards,
        "bestTwoGroceriesCards": bestTwoGroceriesCards,
        "bestTwoOnlineCards": bestTwoOnlineCards,
        "bestTwoDiningCards": bestTwoDiningCards,
        "bestTwoOtherCards": bestTwoOtherCards,
        "bestTwoOverallCards": bestTwoOverallCards
    }
