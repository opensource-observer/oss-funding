# Script Documentation for Grants Pool and Applications URI Generation:

    This script is used to generate two types of JSON files:
    1. **Applications URI JSON**: Contains grant applications data from a CSV file.
    2. **Grants Pool JSON**: Contains metadata about grants pools from a YAML file.

    ### Commands and Options:

    **Basic Usage:**
    ```
    python3 main.py --csv_file <path-to-csv> [--yaml_file <path-to-yaml>] [--generate <applications|grants|both>]
    ```

    ### Arguments:
    - `--csv_file`: **Required**. The path to the CSV file containing project data (e.g., funding amounts, project names, etc.).
    - `--yaml_file`: **Optional**. The path to the YAML file containing metadata (used to generate the grants pool JSON).
    - `--generate`: **Optional**. You can specify what to generate:
      - `applications`: Only generate the Applications URI JSON.
      - `grants`: Only generate the Grants Pool JSON.
      - `both` (default): Generate both the Applications URI and Grants Pool JSON.

    ### Example Commands:

    1. **Generate Only Applications URI JSON**:
    ```
    python3 main.py --csv_file /path/to/projects.csv --generate applications
    ```

    2. **Generate Only Grants Pool JSON** (Requires YAML File):
    ```
    python3 main.py --csv_file /path/to/projects.csv --yaml_file /path/to/metadata.yaml --generate grants
    ```

    3. **Generate Both Applications URI and Grants Pool JSON**:
    ```
    python3 main.py --csv_file /path/to/projects.csv --yaml_file /path/to/metadata.yaml --generate both
    ```

    ### Output:
    - The script will generate the following files in the `./json/` folder:
      - `*_applications_uri.json`: The Applications URI JSON based on the provided CSV data.
      - `*_grants_pool.json`: The Grants Pool JSON based on the provided YAML metadata (if applicable).

    ### File Structure:
    - CSV: Contains project-related data such as funding amount, project name, grant pool name, etc.
    - YAML: Contains metadata about the DAO or organization running the grants program (used for grants pool generation).