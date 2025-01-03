import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ALLO_API_URL = "https://grants-stack-indexer-v2.gitcoin.co/graphql"
OUTPUT_DIR = "json/Allo"  # Directory to save JSON files
BASE_CONTEXT = "http://www.daostar.org/schemas"
GRANT_POOLS_FILE = os.path.join(OUTPUT_DIR, "grant_pools.json")

GRANT_POOLS_QUERY = """
query GetGrantPools($first: Int, $offset: Int) {
  rounds(first: $first, offset: $offset) {
    id
    chainId
    matchTokenAddress
    fundedAmount
    applicationsStartTime
    applicationsEndTime
    roundMetadataCid
    roundMetadata {
      name
      eligibility {
        description
        requirements { requirement }
      }
      support { info }
      logo
      bannerImage
    }
  }
}
"""

APPLICATIONS_QUERY = """
query Applications($filter: ApplicationFilter, $first: Int) {
  applications(filter: $filter, first: $first) {
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
    response.raise_for_status()
    return response.json()

def map_grant_pools(data):
    """
    Convert Allo grant pool data to DAOIP-5 GrantPool JSON-LD schema.
    """
    grant_pools = []

    for round_data in data["data"]["rounds"]:
        round_metadata = round_data.get("roundMetadata", {})
        eligibility = round_metadata.get("eligibility", {})
        support_info = round_metadata.get("support", {}).get("info", "")

        grant_pool = {
            "type": "GrantPool",
            "id": round_data["id"],
            "name": round_metadata.get("name", f"Grant Round {round_data['id']}"),
            "description": eligibility.get("description", ""),
            "isOpen": (
                round_data["applicationsStartTime"] is not None and
                (round_data["applicationsEndTime"] is None or round_data["applicationsEndTime"] > round_data["applicationsStartTime"])
            ),
            "closeDate": round_data["applicationsEndTime"],
            "applicationsURI": f"/allo/applications?roundId={round_data['id']}",
            "contact": support_info if support_info else None,
            "requiredCredentials": [
                req.get("requirement", "")
                for req in eligibility.get("requirements", [])
            ]
        }

        if "roundMetadataCid" in round_data and round_data["roundMetadataCid"]:
            grant_pool["governanceURI"] = f"https://ipfs.io/ipfs/{round_data['roundMetadataCid']}"

        if "logo" in round_metadata and round_metadata["logo"]:
            grant_pool["image"] = round_metadata["logo"]

        if "bannerImage" in round_metadata and round_metadata["bannerImage"]:
            grant_pool["coverImage"] = round_metadata["bannerImage"]

        grant_pools.append(grant_pool)

    return grant_pools

def save_grant_pools(grant_pools):
    """
    Save grant pools to a file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(GRANT_POOLS_FILE, "w") as f:
        json.dump(grant_pools, f, indent=2)

def load_grant_pools():
    """
    Load grant pools from a file.
    """
    if os.path.exists(GRANT_POOLS_FILE):
        with open(GRANT_POOLS_FILE, "r") as f:
            return json.load(f)
    return []

@app.route('/allo/grant-pools', methods=['GET'])
def list_grant_pools():
    """
    Endpoint to list grant pools, paginated by 'first' and 'offset'.
    """
    first = int(request.args.get("first", 10))
    offset = int(request.args.get("offset", 0))

    grant_pools = load_grant_pools()
    paginated_pools = grant_pools[offset:offset + first]

    return jsonify(paginated_pools), 200

@app.route('/allo/applications', methods=['GET'])
def list_applications():
    """
    Endpoint to list applications for a specific grant pool.
    """
    round_id = request.args.get("roundId")
    if not round_id:
        return jsonify({"error": "Missing 'roundId' parameter"}), 400

    try:
        variables = {"filter": {"roundId": {"equalTo": round_id}}, "first": 100}
        data = fetch_allo_data(APPLICATIONS_QUERY, variables)
        applications = []

        for application in data["data"]["applications"]:
            applications.append({
                "type": "GrantApplication",
                "id": application["id"],
                "grantPoolsURI": f"/allo/grant-pools",
                "grantPoolId": round_id,
                "grantPoolName": application["round"]["roundMetadata"].get("name", f"Grant Round {round_id}"),
                "projectsURI": f"https://grants-indexer.gitcoin.co/projects/{application['projectId']}",
                "projectId": application["projectId"],
                "projectName": application["project"].get("name", ""),
                "createdAt": application["metadataCid"],  # ToDO Fix
                "contentURI": f"https://ipfs.io/ipfs/{application['metadataCid']}" if application["metadataCid"] else None,
                "status": application["status"]
            })

        return jsonify(applications), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Fetch grant pools data and save locally
    try:
        grant_pools_data = fetch_allo_data(GRANT_POOLS_QUERY, {"first": 100, "offset": 0})
        grant_pools = map_grant_pools(grant_pools_data)
        save_grant_pools(grant_pools)
        print(f"Grant pools saved at {GRANT_POOLS_FILE}")
    except Exception as e:
        print(f"Error fetching grant pools: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)
