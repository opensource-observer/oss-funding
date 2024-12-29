from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
import time

# Initialize FastAPI app
app = FastAPI()

# Path to the directory where the JSON files are stored (relative to the repository)
BASE_PATH = '../../json'

# Middleware to measure and log response times
class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        response.headers['X-Response-Time'] = f"{latency:.2f} ms"
        print(f"Endpoint: {request.url.path} | Method: {request.method} | Latency: {latency:.2f} ms")
        return response

app.add_middleware(TimerMiddleware)

def get_grant_systems():
    """
    List all grant systems (folders) in the json directory.
    """
    if not os.path.exists(BASE_PATH):
        raise HTTPException(status_code=404, detail="Base path not found")
    return [folder for folder in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, folder))]

def get_grant_pools(grant_system):
    """
    List all JSON files (grant pools) in a given grant system folder.
    """
    folder_path = os.path.join(BASE_PATH, grant_system)
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail=f"Grant system '{grant_system}' not found")
    return [file for file in os.listdir(folder_path) if file.endswith('.json')]

def get_file_path(grant_system, filename):
    """
    Get the file path for the specified JSON file in the grant system folder.
    """
    folder_path = os.path.join(BASE_PATH, grant_system)
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path) or not filename.endswith('.json'):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in '{grant_system}'")

    return file_path

@app.get("/help", response_class=HTMLResponse)
async def display_help():
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
        </div>
        <div class="endpoint">
            <h2>Endpoint: /&lt;grant_system&gt;</h2>
            <p><strong>Method:</strong> GET</p>
            <p><strong>Description:</strong> List all grant pools (JSON files) within a specific grant system folder.</p>
        </div>
        <div class="endpoint">
            <h2>Endpoint: /&lt;grant_system&gt;/&lt;filename&gt;.json</h2>
            <p><strong>Method:</strong> GET</p>
            <p><strong>Description:</strong> Retrieve a specific JSON file within a grant system folder.</p>
        </div>
        <div class="endpoint">
            <h2>Endpoint: /help</h2>
            <p><strong>Method:</strong> GET</p>
            <p><strong>Description:</strong> Display this documentation.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=documentation_html, status_code=200)

@app.get("/")
async def list_all_grant_systems():
    """
    Endpoint to list all grant systems (folders).
    """
    try:
        grant_systems = get_grant_systems()
        return JSONResponse(content=grant_systems, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/{grant_system}")
async def list_grant_pools(grant_system: str):
    """
    Endpoint to list all grant pools (JSON files) in a specific grant system.
    """
    try:
        grant_pools = get_grant_pools(grant_system)
        return JSONResponse(content=grant_pools, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/{grant_system}/{filename}.json")
async def proxy_json_file(grant_system: str, filename: str):
    """
    Endpoint to serve a specific JSON file from a grant system folder (acting as a proxy).
    """
    try:
        file_path = get_file_path(grant_system, f"{filename}.json")
        return FileResponse(file_path, media_type='application/json')
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# To run the application, use the command: uvicorn <filename>:app --reload --host 0.0.0.0 --port 8000
