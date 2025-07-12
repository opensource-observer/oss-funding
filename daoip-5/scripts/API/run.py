from flask import Flask, jsonify, abort, redirect, redirect, send_file
import os
import json
import logging

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
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; line-height: 1.6; }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            h3 { color: #7f8c8d; }
            p { font-size: 1.1em; }
            .endpoint { margin-top: 25px; padding: 15px; border-left: 4px solid #3498db; background-color: #f8f9fa; }
            .param, .response { margin-left: 20px; }
            .method { background-color: #27ae60; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold; }
            .url { font-family: monospace; background-color: #ecf0f1; padding: 2px 4px; border-radius: 3px; }
            .json-example { background-color: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.9em; }
            .warning { background-color: #f39c12; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>DAOIP-5 Datalake API Documentation</h1>
        <p><strong>Repository:</strong> <a href="https://github.com/opensource-observer/oss-funding/tree/main/daoip-5/json" target="_blank">DAOIP-5 JSON Repository</a></p>
        
        <div class="warning">
            <strong>⚠️ Note:</strong> The Allo Protocol endpoint has been deprecated. Use the static JSON files for grant data access.
        </div>

        <h2>API Overview</h2>
        <p>This API provides access to grant funding data following the DAOIP-5 standard. Data is organized by grant systems (foundations/organizations) and includes both grant pool metadata and application details.</p>

        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="url">/</span></h3>
            <p><strong>Description:</strong> List all grant systems (folders) in the JSON directory.</p>
            <p><strong>Parameters:</strong> None</p>
            <p><strong>Response:</strong> A JSON array of grant system names.</p>
            <div class="json-example">
["arbitrumfoundation", "clrfund", "octant-golemfoundation", "optimism", "stellar"]</div>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="url">/&lt;grant_system&gt;</span></h3>
            <p><strong>Description:</strong> List all grant pools (JSON files) within a specific grant system folder.</p>
            <div class="param">
                <p><strong>Parameters:</strong></p>
                <ul>
                    <li><strong>grant_system</strong> (string): The name of the grant system folder to inspect (e.g., "optimism", "arbitrumfoundation").</li>
                </ul>
            </div>
            <div class="response">
                <p><strong>Response:</strong> A JSON array of JSON file names (grant pools) in the specified folder.</p>
                <div class="json-example">
["grants_pool.json", "grants_season_4_applications_uri.json", "retrofunding5_applications_uri.json"]</div>
            </div>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="url">/&lt;grant_system&gt;/&lt;filename&gt;.json</span></h3>
            <p><strong>Description:</strong> Retrieve a specific JSON file within a grant system folder.</p>
            <div class="param">
                <p><strong>Parameters:</strong></p>
                <ul>
                    <li><strong>grant_system</strong> (string): The name of the grant system folder.</li>
                    <li><strong>filename</strong> (string): The name of the JSON file (without .json extension) to retrieve.</li>
                </ul>
            </div>
            <div class="response">
                <p><strong>Response:</strong> The JSON content of the specified file following DAOIP-5 schema.</p>
            </div>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="url">/search/</span></h3>
            <h3><span class="method">GET</span> <span class="url">/search/&lt;project_name&gt;</span></h3>
            <p><strong>Description:</strong> Search for applications across all grant systems by project name.</p>
            <div class="param">
                <p><strong>Parameters:</strong></p>
                <ul>
                    <li><strong>project_name</strong> (string, optional): The name of the project to search for. If omitted, returns all applications.</li>
                </ul>
            </div>
            <div class="response">
                <p><strong>Response:</strong> JSON object containing matching applications with metadata about their source grant system.</p>
            </div>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="url">/help</span></h3>
            <p><strong>Description:</strong> Display this documentation.</p>
            <p><strong>Parameters:</strong> None</p>
            <p><strong>Response:</strong> HTML documentation page.</p>
        </div>

        <h2>Data Quality & Schema</h2>
        <p>All JSON files follow the DAOIP-5 schema standard. Key features:</p>
        <ul>
            <li><strong>Consistent Schema:</strong> All grant systems use standardized field names and types</li>
            <li><strong>Field Mapping:</strong> Each grant system includes a <span class="url">field_mapping.yaml</span> file documenting schema compliance</li>
            <li><strong>Quality Reports:</strong> Data quality reports are available for each grant system</li>
            <li><strong>Validation:</strong> Automated validation ensures data consistency</li>
        </ul>

        <h2>Available Grant Systems</h2>
        <ul>
            <li><strong>arbitrumfoundation:</strong> Arbitrum Foundation grants and incentive programs</li>
            <li><strong>clrfund:</strong> CLR Fund quadratic funding rounds</li>
            <li><strong>dao-drops-dorgtech:</strong> DAO Drops funding rounds</li>
            <li><strong>octant-golemfoundation:</strong> Octant (Golem Foundation) funding epochs</li>
            <li><strong>optimism:</strong> Optimism Foundation grants and RetroPGF rounds</li>
            <li><strong>stellar:</strong> Stellar Development Foundation community fund rounds</li>
        </ul>

        <h2>Example Usage</h2>
        <div class="json-example">
# Get all grant systems
curl https://your-api-domain.com/

# Get Optimism grant pools
curl https://your-api-domain.com/optimism

# Get specific grant pool data
curl https://your-api-domain.com/optimism/grants_pool.json

# Search for a specific project
curl https://your-api-domain.com/search/uniswap</div>
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
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]
    return json_files



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


@app.route('/search/', defaults={'project_name': ''})
@app.route('/search/<project_name>')
def search_project(project_name):
    """
    Endpoint to search for all applications matching a project name across all grant systems.
    If no project name or empty string is provided, returns all applications.

    Args:
        project_name (str): The name of the project to search for (optional)
    Returns:
        JSON object containing matching applications and result count
    """
    try:
        results = []
        # Use existing function to get grant systems
        grant_systems = get_grant_systems()

        for system in grant_systems:
            # Use existing function to get grant pools
            files = get_grant_pools(system)
            applications_files = [f for f in files if 'applications' in f]

            for file in applications_files:
                try:
                    # Use existing function to get file path and Flask's send_file
                    file_path = get_file_path(system, file)
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    if not isinstance(data, dict) or 'grant_pools' not in data:
                        continue

                    for pool in data['grant_pools']:
                        if not isinstance(pool, dict) or 'applications' not in pool:
                            continue

                        for app in pool['applications']:
                            # If project_name is empty or None, include all applications
                            if not project_name:
                                result = {
                                    **app,
                                    'metadata': {
                                        'grantSystem': system,
                                        'sourceFile': file,
                                        'grantPoolId': app.get('grantPoolId', 'unknown'),
                                        'grantPoolName': app.get('grantPoolName', 'unknown')
                                    }
                                }
                                results.append(result)
                            else:
                                # More robust project name matching for specific search
                                project_name_match = str(app.get('projectName', '')).lower()
                                project_id_match = str(app.get('projectId', '')).lower()
                                search_term = project_name.lower()

                                if search_term in project_name_match or search_term in project_id_match:
                                    result = {
                                        **app,
                                        'metadata': {
                                            'grantSystem': system,
                                            'sourceFile': file,
                                            'grantPoolId': app.get('grantPoolId', 'unknown'),
                                            'grantPoolName': app.get('grantPoolName', 'unknown')
                                        }
                                    }
                                    results.append(result)

                except (json.JSONDecodeError, Exception) as e:
                    # Log the error but continue processing other files
                    logging.error(f"Error processing {file} in {system}: {str(e)}")
                    continue

        search_description = "all applications" if not project_name else f"applications for project: {project_name}"
        response = {
            "message": f"Found {len(results)} {search_description}",
            "count": len(results),
            "results": results
        }
        return jsonify(response), 200

    except Exception as e:
        error_description = "all applications" if not project_name else f"project: {project_name}"
        logging.error(f"Search failed for {error_description}: {str(e)}")
        return jsonify({
            "error": f"Search failed for {error_description}: {str(e)}",
            "status": "error"
        }), 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
