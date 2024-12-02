
# DAOIP-5 Grant Pool URI and Applications URI JSON Generator

This script crawls a given folder path, finds YAML and CSV files, and generates structured JSON files based on the DAO grant pool and applications. The JSON files are stored in a newly created folder under `./datalake/oss-funding/daoip-5/json`, named after the last part of the provided folder path.

## Features

- **YAML Parsing**: The script finds a YAML file at the root of the provided folder path. The YAML file contains metadata about the DAO and its grant pools.
- **CSV Processing**: The script looks for CSV files inside a folder called `uploads` under the provided path. These CSV files hold data about grant applications.
- **JSON Generation**: Based on the data from the YAML and CSV files, the script generates two types of JSON files:
  - **Grant Pool JSON**: Contains metadata about the DAO and its grant pools.
  - **Applications JSON**: Contains structured information about the grant applications.
- **Custom Folder Structure**: The generated JSON files are saved in `./datalake/oss-funding/daoip-5/json/<folder-name>`, where `<folder-name>` is the last part of the provided folder path.

## Prerequisites

- **Python 3.x**
- Required Python libraries:
  - `csv`
  - `json`
  - `yaml`
  - `argparse`
  - `os`

Install the required `yaml` library using pip:

```bash
pip install pyyaml
```

## Usage

### Command Structure

```bash
python3 main.py --path "<path-to-your-folder>"
```

Where:
- `--path` is the root path to the folder containing the YAML and CSV files.

### Example

```bash
python3 main.py --path "./datalake/oss-funding/data/funders/stellar"
```

This command:
1. Crawls through `./datalake/oss-funding/data/funders/stellar`.
2. Finds the YAML file at the root and the CSV files inside `/uploads`.
3. Generates JSON files based on the contents of these files.
4. Saves the generated JSON files in `./datalake/oss-funding/daoip-5/json/stellar`.

## Directory and File Structure

- **Input**: The script expects the following folder structure:
  
  ```
  <provided-path>
  ├── metadata.yaml          # YAML file at the root
  └── uploads/
      └── applications.csv   # CSV files inside 'uploads' folder
  ```

- **Output**: The JSON files will be saved in the following structure:

  ```
  /home/torch/datalake/oss-funding/daoip-5/json/<last-part-of-path>/
  ├── applications_uri.json  # Generated Applications JSON
  └── grants_pool.json       # Generated Grants Pool JSON
  ```

For example, if you provide the path `./datalake/oss-funding/data/funders/stellar`, the output files will be:
Note: Input Absoulute Path
```
/home/torch/datalake/oss-funding/daoip-5/json/stellar/applications_uri.json
/home/torch/datalake/oss-funding/daoip-5/json/stellar/grants_pool.json
```
#### Support
For any support or questions, contact: rashmi@daostar.org