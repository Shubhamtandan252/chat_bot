from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = '6074119cee1823468dde2a96'
BASE_API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/'

# GET route for testing if the server is up
@app.route('/', methods=['GET'])
def home():
    return "Currency conversion API is running. Send a POST request to use it!"

# POST route for Dialogflow or API calls
@app.route('/', methods=['POST'])
def index():
    data = request.get_json()

    # Extracting information from the Dialogflow request
    source_currency = data['queryResult']['parameters']['unit-currency']['currency']  # Base currency
    amount = data['queryResult']['parameters']['unit-currency']['amount']
    target_currency = data['queryResult']['parameters']['currency-name']  # Currency to convert to

    # Fetch the conversion factor based on user-provided base currency
    conversion_rate = fetch_conversion_factor(source_currency, target_currency)
    if conversion_rate is None:
        response = {
            'fulfillmentText': f"Sorry, I couldn't find the conversion rate from {source_currency} to {target_currency}."
        }
        return jsonify(response)

    # Calculate the converted amount
    final_amount = round(amount * conversion_rate, 2)

    response = {
        'fulfillmentText': f"{amount} {source_currency} is {final_amount} {target_currency}."
    }
    return jsonify(response)

def fetch_conversion_factor(base_currency, target_currency):
    url = BASE_API_URL + base_currency  # Base currency dynamically included
    try:
        response = requests.get(url)
        data = response.json()

        # Check for API success
        if data['result'] != 'success':
            print("API error:", data.get('error-type'))
            return None

        # Get the rates dictionary
        rates = data['conversion_rates']

        # Look for the target currency in the rates
        if target_currency in rates:
            return rates[target_currency]
        else:
            print(f"Target currency {target_currency} not found in rates.")
            return None

    except Exception as e:
        print("Error fetching conversion factor:", str(e))
        return None

if __name__ == "__main__":
    app.run(debug=True)
