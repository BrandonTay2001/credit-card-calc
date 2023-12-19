from flask import Flask
from flask import request
from calculate import calculate

app = Flask(__name__)

@app.route('/calculate', methods=['POST'])
def calculate():
    # get request json, fields: petrol, groceries, utilities, dining, other
    petrolSpending = request.json['petrol']
    groceriesSpending = request.json['groceries']
    onlineSpending = request.json['online']
    diningSpending = request.json['dining']
    otherSpending = request.json['other']
    try:
        calculatedValues = calculate(petrolSpending, groceriesSpending, onlineSpending, diningSpending, otherSpending)
        return calculatedValues
    except:
        return "Error calculating"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)