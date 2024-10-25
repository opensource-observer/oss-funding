from flask import Flask, jsonify, abort, send_file
import os

app = Flask(__name__)

# Path to the directory where the JSON files are stored (relative to the repository)
BASE_PATH = '../../json'  


def get_grant_systems():
    """
    List all grant systems (folders) in the json directory.
    """
    return [folder for folder in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, folder))]

@app.route('/help', methods=['GET'])
def display_help():
    """
    Endpoint to display API documentation.
    """
    documentation = {
        "title": "DAOIP-5 Datalake API",
        "repository": "https://github.com/opensource-observer/oss-funding/tree/main/daoip-5/json",
        "endpoints": {
            "/": {
                "method": "GET",
                "description": "List all grant systems (folders) in the JSON directory.",
                "parameters": None,
                "response": "A JSON array of grant system names."
            },
            "/<grant_system>": {
                "method": "GET",
                "description": "List all grant pools (JSON files) within a specific grant system folder.",
                "parameters": {
                    "grant_system": "string - The name of the grant system folder to inspect."
                },
                "response": "A JSON array of JSON file names (grant pools) in the specified folder."
            },
            "/<grant_system>/<filename>.json": {
                "method": "GET",
                "description": "Retrieve a specific JSON file within a grant system folder.",
                "parameters": {
                    "grant_system": "string - The name of the grant system folder.",
                    "filename": "string - The name of the JSON file (without .json extension) to retrieve."
                },
                "response": "The JSON content of the specified file."
            },
            "/help": {
                "method": "GET",
                "description": "Display this documentation.",
                "parameters": None,
                "response": "A JSON object detailing all API endpoints and their descriptions."
            }
        }
    }
    return jsonify(documentation), 200



def get_grant_pools(grant_system):
    """
    List all JSON files (grant pools) in a given grant system folder.
    """
    folder_path = os.path.join(BASE_PATH, grant_system)
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        abort(404, description=f"Grant system '{grant_system}' not found")

    # List all .json files in the folder
    return [file for file in os.listdir(folder_path) if file.endswith('.json')]


def get_file_path(grant_system, filename):
    """
    Get the file path for the specified JSON file in the grant system folder.
    """
    folder_path = os.path.join(BASE_PATH, grant_system)
    file_path = os.path.join(folder_path, filename)

    # Check if the file exists and is a .json file
    if not os.path.exists(file_path) or not filename.endswith('.json'):
        abort(404, description=f"File '{filename}' not found in '{grant_system}'")

    return file_path


@app.route('/', methods=['GET'])
def list_all_grant_systems():
    """
    Endpoint to list all grant systems (folders).
    """
    try:
        grant_systems = get_grant_systems()
        return jsonify(grant_systems), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/<grant_system>', methods=['GET'])
def list_grant_pools(grant_system):
    """
    Endpoint to list all grant pools (JSON files) in a specific grant system.
    """
    try:
        grant_pools = get_grant_pools(grant_system)
        return jsonify(grant_pools), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/<grant_system>/<filename>.json', methods=['GET'])
def proxy_json_file(grant_system, filename):
    """
    Endpoint to serve a specific JSON file from a grant system folder (acting as a proxy).
    """
    try:
        file_path = get_file_path(grant_system, f"{filename}.json")
        return send_file(file_path, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)