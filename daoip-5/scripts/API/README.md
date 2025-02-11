# DAOIP-5 Datalake API

This Flask application provides a simple API to explore and retrieve JSON files stored in a directory structure representing different grant systems. The API allows users to list available grant systems, view grant pools within each system, and access specific JSON files. It also includes a `/help` endpoint that provides documentation for all API routes.

## Repository
GitHub repository: [DAOIP-5 JSON files](https://github.com/opensource-observer/oss-funding/tree/main/daoip-5/json)

## Setup and Installation

### Prerequisites
- Python 3.x
- Flask

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/opensource-observer/oss-funding
   cd oss-funding/daoip-5
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To start the Flask app, run:

```bash
python3 run.py
```

The application will be available on `http://0.0.0.0:5000` by default.

## API Endpoints

### 1. **List All Grant Systems**
   - **URL**: `/`
   - **Method**: `GET`
   - **Description**: Lists all available grant systems, which are directories in the `json` folder.
   - **Response**: JSON array of grant system names (folders).

### 2. **List Grant Pools in a Grant System**
   - **URL**: `/<grant_system>`
   - **Method**: `GET`
   - **Description**: Lists all grant pools (JSON files) in the specified grant system folder.
   - **Parameters**:
     - `grant_system` (string) - The name of the grant system folder to inspect.
   - **Response**: JSON array of JSON file names within the specified grant system.

### 3. **Retrieve Specific Grant Pool JSON File**
   - **URL**: `/<grant_system>/<filename>.json`
   - **Method**: `GET`
   - **Description**: Serves a specific JSON file within a grant system folder.
   - **Parameters**:
     - `grant_system` (string) - The name of the grant system folder.
     - `filename` (string) - The name of the JSON file (without the `.json` extension).
   - **Response**: The content of the specified JSON file.

### 4. **API Documentation**
   - **URL**: `/help`
   - **Method**: `GET`
   - **Description**: Provides a JSON object documenting all API endpoints, including descriptions and parameter details.
   - **Response**: JSON object containing documentation for all endpoints.

## Directory Structure

The JSON files should be organized under `../../json` relative to the script, with the structure:
```
json/
├── grant_system_1/
│   ├── file1.json
│   ├── file2.json
│   └── ...
├── grant_system_2/
│   ├── file1.json
│   └── ...
└── ...
```

## License

This project is licensed under the [MIT License](LICENSE).
