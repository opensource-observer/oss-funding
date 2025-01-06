from flask import Flask, jsonify, abort, send_file
import os
from x_to_DAOIP5.allo_to_DAOIP5 import allo_blueprint


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
    documentation_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DAOIP-5 Datalake API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            h2 { color: #0056b3; }
            p { font-size: 1.1em; }
            .endpoint { margin-top: 20px; }
            .param, .response { margin-left: 20px; }
        </style>
    </head>
    <body>
        <h1>DAOIP-5 Datalake API Documentation</h1>
        <p><strong>Repository:</strong> <a href="https://github.com/opensource-observer/oss-funding/tree/main/daoip-5/json" target="_blank">DAOIP-5 JSON Repository</a></p>
        
        <div class="endpoint">
            <h2>Endpoint: /</h2>
            <p><strong>Method:</strong> GET</p>
            <p><strong>Description:</strong> List all grant systems (folders) in the JSON directory.</p>
            <p><strong>Parameters:</strong> None</p>
            <p><strong>Response:</strong> A JSON array of grant system names.</p>
        </div>
        
        <div class="endpoint">
            <h2>Endpoint: /&lt;grant_system&gt;</h2>
            <p><strong>Method:</strong> GET</p>
            <p><strong>Description:</strong> List all grant pools (JSON files) within a specific grant system folder.</p>
            <div class="param">
                <p><strong>Parameters:</strong></p>
                <ul>
                    <li><strong>grant_system</strong> (string): The name of the grant system folder to inspect.</li>
                </ul>
            </div>
            <div class="response">
                <p><strong>Response:</strong> A JSON array of JSON file names (grant pools) in the specified folder.</p>
            </div>
        </div>
        
        <div class="endpoint">
            <h2>Endpoint: /&lt;grant_system&gt;/&lt;filename&gt;.json</h2>
            <p><strong>Method:</strong> GET</p>
            <p><strong>Description:</strong> Retrieve a specific JSON file within a grant system folder.</p>
            <div class="param">
                <p><strong>Parameters:</strong></p>
                <ul>
                    <li><strong>grant_system</strong> (string): The name of the grant system folder.</li>
                    <li><strong>filename</strong> (string): The name of the JSON file (without .json extension) to retrieve.</li>
                </ul>
            </div>
            <div class="response">
                <p><strong>Response:</strong> The JSON content of the specified file.</p>
            </div>
        </div>
        
        <div class="endpoint">
            <h2>Endpoint: /help</h2>
            <p><strong>Method:</strong> GET</p>
            <p><strong>Description:</strong> Display this documentation.</p>
            <p><strong>Parameters:</strong> None</p>
            <p><strong>Response:</strong> A JSON object detailing all API endpoints and their descriptions.</p>
        </div>
        
         <div class="endpoint">
            <h2>Endpoint: /allo/grant_pools.json</h2>
            <p><strong>Method:</strong> GET</p>
            <p><strong>Description:</strong> Display Allo Grant Pools</p>
            <p><strong>Parameters:</strong> None</p>
            <p><strong>Response:</strong> A JSON object detailing grant pools</p>
        </div>
    </body>
    </html>
    """
    return documentation_html, 200, {'Content-Type': 'text/html'}


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

# /allo endpoint
app.register_blueprint(allo_blueprint, url_prefix='/allo')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
