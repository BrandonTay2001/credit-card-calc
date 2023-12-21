from flask import Flask
from flask import request

from calculate_cashback import calculate_cashback  # Import the calculate function from the calculate module

app = Flask(__name__)

@app.route('/calculate', methods=['POST'])
def calculate():
    # get request json, fields: petrol, groceries, utilities, dining, other
    petrolSpending = int(request.json['petrol'])
    groceriesSpending = int(request.json['groceries'])
    onlineSpending = int(request.json['online'])
    diningSpending = int(request.json['dining'])
    otherSpending = int(request.json['other'])
    print(petrolSpending, groceriesSpending, onlineSpending, diningSpending, otherSpending)
    try:
        calculatedValues = calculate_cashback(petrolSpending, groceriesSpending, onlineSpending, diningSpending, otherSpending)
        print(calculatedValues)
        return calculatedValues, 200  # OK status code
    except Exception as e:  # Handle any exceptions that may occur during the calculation process
        print(e)
        return "Error calculating", 500  # Internal Server Error status code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)