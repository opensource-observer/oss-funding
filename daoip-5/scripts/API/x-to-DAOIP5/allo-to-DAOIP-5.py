import json
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify

app = Flask(__name__)

ALLO_API_URL = "https://grants-stack-indexer-v2.gitcoin.co/graphql"

GRANT_POOLS_QUERY = """
query GetGrantPools($first: Int, $offset: Int) {
  rounds(first: $first, offset: $offset) {
    id
    chainId
    matchTokenAddress
    fundedAmount
    applicationsEndTime
    roundMetadataCid
    roundMetadata
  }
}
"""

APPLICATIONS_QUERY = """
query Applications($filter: ApplicationFilter, $first: Int, $offset: Int) {
  applications(filter: $filter, first: $first, offset: $offset) {
    id
    chainId
    metadataCid
    projectId
    project {
      name
    }
    round {
      id
      roundMetadataCid
      roundMetadata
    }
    status
    totalAmountDonatedInUsd
    uniqueDonorsCount
  }
}
"""

def fetch_allo_data(query, variables):
    """
    Fetch data from the Allo protocol's GraphQL API.
    """
    headers = {"Content-Type": "application/json"}
    response = requests.post(ALLO_API_URL, json={"query": query, "variables": variables}, headers=headers)

    # Log the full response for debugging
    try:
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Response content:", response.content.decode())  # Log response details
        return {}

def map_grant_pool(pool_data):
    """
    Map individual grant pool data to the DAOIP-5 schema.
    """
    round_metadata = pool_data.get("roundMetadata", {}) or {}
    applications_end_time = pool_data.get("applicationsEndTime")
    is_open = True  # Default to True if applicationsEndTime is missing or invalid

    if applications_end_time:
        try:
            end_time = datetime.fromisoformat(applications_end_time)
            is_open = datetime.now(timezone.utc) < end_time
        except (ValueError, OverflowError):
            print(f"Invalid or out-of-range date format for applicationsEndTime: {applications_end_time}")

    return {
        "type": "GrantPool",
        "id": pool_data["id"],
        "name": round_metadata.get("name", f"Grant Round {pool_data['id']}"),
        "description": round_metadata.get("description", ""),
        "isOpen": is_open,
        "closeDate": applications_end_time,
        "applicationsURI": f"https://daoip5.daostar.org/allo/applications?roundId={pool_data['id']}",
        "contact": round_metadata.get("support", {}).get("info", None),
        "requiredCredentials": [
            req.get("requirement", "")
            for req in round_metadata.get("eligibility", {}).get("requirements", [])
        ],
        "governanceURI": f"https://ipfs.io/ipfs/{pool_data['roundMetadataCid']}" if pool_data.get("roundMetadataCid") else None,
        "image": round_metadata.get("logo"),
        "coverImage": round_metadata.get("bannerImage"),
    }

def map_application(application, grant_pool_id):
    """
    Map individual application data to the required schema.
    """
    return {
        "type": "GrantApplication",
        "id": application["id"],
        "grantPoolsURI": "https://daoip5.daostar.org/allo/grant_pools.json",
        "grantPoolId": grant_pool_id,
        "grantPoolName": application["round"]["roundMetadata"].get("name", f"Grant Round {grant_pool_id}"),
        "projectsURI": f"https://grants-indexer.gitcoin.co/projects/{application['projectId']}",
        "projectId": application["projectId"],
        "projectName": application["project"].get("name", ""),
        "createdAt": application.get("metadataCid"),  # Assuming metadataCid holds creation time
        "contentURI": f"https://ipfs.io/ipfs/{application['metadataCid']}" if application["metadataCid"] else None,
        "discussionsTo": None,  # Placeholder for discussions URI
        "fundsAsked": [],  # Placeholder for funds asked
        "fundsApproved": [],  # Placeholder for funds approved
        "payoutAddress": {
            "type": "EthereumAddress",
            "value": "0x0"  # Placeholder, replace with actual payout address if available
        },
        "isEligible": None,
        "isReviewed": None,
        "isApproved": None,
        "isPaid": None,
        "payouts": []  # Placeholder for payouts
    }



@app.route('/allo/grant_pools.json', methods=['GET'])
def list_grant_pools():
    """
    Endpoint to display the grant pools JSON with paginated grantPools.
    """
    first = int(request.args.get("first", 10))
    offset = int(request.args.get("offset", 0))

    api_data = fetch_allo_data(GRANT_POOLS_QUERY, {"first": first, "offset": offset})
    pools = api_data.get("rounds", [])
    grant_pools = [map_grant_pool(pool) for pool in pools]

    response = {
        "@context": "http://www.daostar.org/schemas",
        "name": "Allo Protocol",
        "type": "Entity",
        "grantPools": grant_pools,
        "pagination": {
            "first": first,
            "offset": offset,
            "returned": len(grant_pools),
        }
    }
    return jsonify(response), 200

@app.route('/allo/applications', methods=['GET'])
def list_applications():
    """
    Endpoint to list applications for a specific grant pool with pagination and required schema.
    """
    round_id = request.args.get("roundId")
    first = int(request.args.get("first", 10))
    offset = int(request.args.get("offset", 0))

    if not round_id:
        return jsonify({"error": "Missing 'roundId' parameter"}), 400

    # Fetch applications dynamically
    variables = {"filter": {"roundId": {"equalTo": round_id}}, "first": first, "offset": offset}
    api_data = fetch_allo_data(APPLICATIONS_QUERY, variables)
    applications = api_data.get("applications", [])

    # Extract grant pool name from roundMetadata
    grant_pool_name = "Unknown Grant Pool"
    for app in applications:
        if "round" in app and "roundMetadata" in app["round"]:
            grant_pool_name = app["round"]["roundMetadata"].get("name", f"Grant Pool for {round_id}")
            break

    mapped_applications = [
        map_application(app, round_id) for app in applications
    ]

    response = {
        "@context": "http://www.daostar.org/schemas",
        "name": "Allo Protocol Applications",
        "type": "Entity",
        "grantPools": [
            {
                "type": "GrantPool",
                "id": round_id,
                "name": grant_pool_name,
                "applications": mapped_applications
            }
        ],
        "pagination": {
            "first": first,
            "offset": offset,
            "returned": len(mapped_applications),
        }
    }
    return jsonify(response), 200



@app.route('/', methods=['GET'])
def index():
    """
    Display API documentation at the root endpoint.
    """
    return jsonify({
        "message": "Welcome to the Allo DAOIP-5 API",
        "endpoints": {
            "/allo/grant-pools": "GET endpoint to list grant pools, supports pagination with 'first' and 'offset' params.",
            "/allo/applications": "GET endpoint to list applications for a specific grant pool. Requires 'roundId' as a query parameter.",
        }
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)