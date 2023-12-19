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

class LimitedHeap:
    def __init__(self, limit):
        self.limit = limit
        self.heap = []

    def push(self, item):
        if len(self.heap) < self.limit:
            heapq.heappush(self.heap, item)
        else:
            heapq.heappushpop(self.heap, item)

    def get_heap(self):
        return self.heap

def calculate_cashback_for_category(spend_amount, tiers):
    cashback = 0
    for tier in tiers:
        if spend_amount >= tier["spend"][1]:
            cashback += tier["monthly_cap"]
        elif spend_amount >= tier["spend"][0] and spend_amount < tier["spend"][1]:
            cashback += min(tier["cashback_percentage"] / 100 * (spend_amount - tier["spend"][0]), 
                            tier["monthly_cap"])
            break
    cashback = round(cashback, 2)  # Round to 2 decimal places
    return cashback

def calculate(petrolSpending, groceriesSpending, onlineSpending, diningSpending, otherSpending):
    category_to_spend = {
        "Petrol": petrolSpending, "Groceries": groceriesSpending, "Online": onlineSpending,
        "Dining": diningSpending, "Other": otherSpending
    }
    
    # get all cards in db
    cards = col.find({})
    bestTwoPetrol, bestTwoGroceries, bestTwoOnline, bestTwoDining, bestTwoOther = LimitedHeap(2), LimitedHeap(2), LimitedHeap(2), LimitedHeap(2), LimitedHeap(2)
    card_to_total_cashback = {}
    
    # calculate cashback by category
    for card in cards:  # each card
        for cat_group in card['categories']:    # each category
            if "Petrol" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Petrol"], cat_group["tier"])
                bestTwoPetrol.push((-cat_cashback, card["name"]))
            if "Groceries" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Groceries"], cat_group["tier"])
                bestTwoGroceries.push((-cat_cashback, card["name"]))
            if "Online" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Online"], cat_group["tier"])
                bestTwoOnline.push((-cat_cashback, card["name"]))
            if "Dining" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Dining"], cat_group["tier"])
                bestTwoDining.push((-cat_cashback, card["name"]))
            if "Other" in cat_group["individual_categories"]:
                cat_cashback = calculate_cashback_for_category(category_to_spend["Other"], cat_group["tier"])
                bestTwoOther.push((-cat_cashback, card["name"])) 

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
    bestTwoOverallCards = heapq.nlargest(2, card_to_total_cashback, key=card_to_total_cashback.get)

    return {
        "bestTwoPetrolCards": bestTwoPetrolCards,
        "bestTwoGroceriesCards": bestTwoGroceriesCards,
        "bestTwoOnlineCards": bestTwoOnlineCards,
        "bestTwoDiningCards": bestTwoDiningCards,
        "bestTwoOtherCards": bestTwoOtherCards,
        "bestTwoOverallCards": bestTwoOverallCards
    }