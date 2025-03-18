from flask import Flask, jsonify
import requests
import datetime

app = Flask(__name__)

GIVETH_API_URL = "https://mainnet.serve.giveth.io/graphql"
GIVETH_QUERY = """
{
  qfRounds(activeOnly: false) {
    id
    name
    description
    slug
    allocatedFundUSD
    allocatedFundUSDPreferred
    beginDate
    endDate
    qfStrategy
  }
}
"""

def fetch_giveth_data():
    response = requests.post(GIVETH_API_URL, json={'query': GIVETH_QUERY})
    if response.status_code == 200:
        return response.json()['data']['qfRounds']
    else:
        return None

def transform_to_daoip5(giveth_rounds):
    daoip5_data = {
        "@context": "http://www.daostar.org/schemas",
        "name": "Giveth Grant Pools",
        "type": "DAO",
        "grantPools": []
    }

    for round in giveth_rounds:
        begin_date = round['beginDate']
        close_date = round['endDate']
        is_open = close_date is None or datetime.datetime.fromisoformat(close_date[:-1]) > datetime.datetime.utcnow()
        
        grant_pool = {
            "type": "GrantPool",
            "id": f"giveth-round-{round['id']}",
            "name": round['name'],
            "description": round['description'] if round['description'] else "No description provided.",
            "grantPoolType": round['qfStrategy'],
            "isOpen": is_open,
            "beginDate" : begin_date,
            "closeDate": close_date,
            "applicationsURI": f"",
            "governanceURI": f"",
        }
        daoip5_data['grantPools'].append(grant_pool)

    return daoip5_data

@app.route('/', methods=['GET'])
def hello():
    return jsonify("GIVETH API")

@app.route('/grantPools', methods=['GET'])
def get_grant_pools():
    giveth_rounds = fetch_giveth_data()
    if giveth_rounds:
        daoip5_data = transform_to_daoip5(giveth_rounds)
        return jsonify(daoip5_data)
    else:
        return jsonify({"error": "Failed to fetch data from Giveth API"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
