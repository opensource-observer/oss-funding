from flask import Flask, jsonify, abort, redirect, redirect, send_file
import os
import json
import logging
from functools import lru_cache
from threading import Lock
import time

app = Flask(__name__)

# Path to the directory where the JSON files are stored (relative to the repository)
BASE_PATH = '../../json'

# Global cache for file data and metadata
_file_cache = {}
_cache_lock = Lock()
_cache_ttl = 300  # 5 minutes TTL


def _is_cache_valid(cache_entry):
    """Check if cache entry is still valid based on TTL"""
    return time.time() - cache_entry['timestamp'] < _cache_ttl

def _get_file_modified_time(file_path):
    """Get file modification time"""
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0

@lru_cache(maxsize=32)
def get_grant_systems():
    """
    List all grant systems (folders) in the json directory.
    Cached for performance.
    """
    try:
        return [folder for folder in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, folder))]
    except OSError as e:
        logging.error(f"Error listing grant systems: {e}")
        return []

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

    </body>
    </html>
    """
    return documentation_html, 200, {'Content-Type': 'text/html'}


def get_grant_pools(grant_system):
    """
    List all JSON files (grant pools) in a given grant system folder.
    Cached for performance.
    """
    cache_key = f"pools_{grant_system}"
    
    with _cache_lock:
        if cache_key in _file_cache and _is_cache_valid(_file_cache[cache_key]):
            return _file_cache[cache_key]['data']
    
    folder_path = os.path.join(BASE_PATH, grant_system)
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        abort(404, description=f"Grant system '{grant_system}' not found")
    
    try:
        json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]
        
        with _cache_lock:
            _file_cache[cache_key] = {
                'data': json_files,
                'timestamp': time.time()
            }
        
        return json_files
    except OSError as e:
        logging.error(f"Error listing grant pools for {grant_system}: {e}")
        abort(500, description="Internal server error")



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

def get_cached_json_file(grant_system, filename):
    """
    Get JSON file content with caching and modification time checking.
    """
    file_path = get_file_path(grant_system, filename)
    cache_key = f"json_{grant_system}_{filename}"
    file_mtime = _get_file_modified_time(file_path)
    
    with _cache_lock:
        if cache_key in _file_cache:
            cache_entry = _file_cache[cache_key]
            if (cache_entry['mtime'] == file_mtime and 
                _is_cache_valid(cache_entry)):
                return cache_entry['data']
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with _cache_lock:
            _file_cache[cache_key] = {
                'data': data,
                'mtime': file_mtime,
                'timestamp': time.time()
            }
        
        return data
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        abort(500, description="Error loading file")


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
    Optimized endpoint to serve JSON files using cached loading.
    """
    try:
        data = get_cached_json_file(grant_system, f"{filename}.json")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/search/', defaults={'project_name': ''})
@app.route('/search/<project_name>')
def search_project(project_name):
    """
    Optimized endpoint to search for applications across all grant systems.
    Uses caching and early termination for better performance.
    """
    try:
        results = []
        search_term = project_name.lower() if project_name else None
        grant_systems = get_grant_systems()
        
        # Early termination for specific searches with limit
        max_results = 1000 if not project_name else 100

        for system in grant_systems:
            try:
                files = get_grant_pools(system)
                applications_files = [f for f in files if 'applications' in f.lower()]

                for file in applications_files:
                    try:
                        # Use cached JSON loading
                        data = get_cached_json_file(system, file)

                        # Support both 'grant_pools' and 'grantPools' naming
                        pools = data.get('grant_pools') or data.get('grantPools', [])
                        if not isinstance(pools, list):
                            continue

                        for pool in pools:
                            if not isinstance(pool, dict) or 'applications' not in pool:
                                continue

                            applications = pool.get('applications', [])
                            if not isinstance(applications, list):
                                continue

                            for app in applications:
                                if len(results) >= max_results:
                                    break
                                
                                # If no search term, include all applications
                                if not search_term:
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
                                    # Optimized string matching
                                    project_name_str = str(app.get('projectName', '')).lower()
                                    project_id_str = str(app.get('projectId', '')).lower()

                                    if (search_term in project_name_str or 
                                        search_term in project_id_str):
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
                            
                            if len(results) >= max_results:
                                break
                        
                        if len(results) >= max_results:
                            break

                    except Exception as e:
                        logging.error(f"Error processing {file} in {system}: {str(e)}")
                        continue
                
                if len(results) >= max_results:
                    break

            except Exception as e:
                logging.error(f"Error processing system {system}: {str(e)}")
                continue

        search_description = "all applications" if not project_name else f"applications for project: {project_name}"
        truncated = len(results) >= max_results
        
        response = {
            "message": f"Found {len(results)} {search_description}",
            "count": len(results),
            "truncated": truncated,
            "results": results
        }
        
        if truncated:
            response["message"] += f" (limited to {max_results} results)"
        
        return jsonify(response), 200

    except Exception as e:
        error_description = "all applications" if not project_name else f"project: {project_name}"
        logging.error(f"Search failed for {error_description}: {str(e)}")
        return jsonify({
            "error": f"Search failed for {error_description}: {str(e)}",
            "status": "error"
        }), 500



@app.route('/admin/clear-cache', methods=['POST'])
def clear_cache():
    """
    Administrative endpoint to clear the internal cache.
    """
    try:
        with _cache_lock:
            _file_cache.clear()
        get_grant_systems.cache_clear()
        return jsonify({"message": "Cache cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/cache-stats', methods=['GET'])
def cache_stats():
    """
    Administrative endpoint to get cache statistics.
    """
    try:
        with _cache_lock:
            cache_info = {
                "cache_entries": len(_file_cache),
                "cache_ttl_seconds": _cache_ttl,
                "grant_systems_cache_info": get_grant_systems.cache_info()._asdict()
            }
        return jsonify(cache_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Configure logging for better performance monitoring
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Warm up cache with grant systems
    try:
        get_grant_systems()
        logging.info("Cache warmed up successfully")
    except Exception as e:
        logging.error(f"Cache warmup failed: {e}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port, threaded=True)
