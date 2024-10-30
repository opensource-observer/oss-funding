import json
import numpy as np
import os
import pandas as pd


DATA_DIR = 'data'
OUT_NAME = 'funding_data'
REQ_COLS = ['to_project_name', 'amount', 'funding_date', 
            'from_funder_name', 'grant_pool_name', 'metadata']


def load_funding_csv(csv_file_path):
    try:
        csv = pd.read_csv(csv_file_path)
        csv = csv[REQ_COLS]
        csv['file_path'] = csv_file_path
        print("Loaded CSV at:", csv_file_path)
        return csv
    except Exception as e:
        print(f"Error reading {csv_file_path}: {e}")
        return pd.DataFrame()
    

def walk_funding_csvs(data_dir, ignore_list=[]):
    dataframes = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.lower().endswith('.csv'):
                file_path = os.path.join(root, file)
                if file_path not in ignore_list:
                    csv = load_funding_csv(file_path)                    
                    dataframes.append(csv)

    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return pd.DataFrame()
        print("No CSV files found.")


def json_export(dataframe, json_outpath):
    dataframe['amount'] = dataframe['amount'].fillna(0)
    dataframe['funding_date'] = dataframe['funding_date'].fillna("")
    data = dataframe.to_dict(orient='records')
    for grant in data:
        if not isinstance(grant['to_project_name'], str):
            grant['to_project_name'] = None
        try:
            grant['metadata'] = json.loads(grant['metadata'])
        except json.JSONDecodeError:
            print(f"Invalid JSON in metadata: {grant['metadata']}")
            grant['metadata'] = {}
    with open(json_outpath, 'w') as json_file:
        json.dump(data, json_file, indent=2)
    print("Exported to", json_outpath)
    

def main():

    csv_outpath = os.path.join(DATA_DIR, OUT_NAME + '.csv')
    json_outpath = os.path.join(DATA_DIR, OUT_NAME + '.json')

    df = walk_funding_csvs(DATA_DIR, ignore_list=[csv_outpath])
    json_export(df, json_outpath)

    df.set_index(REQ_COLS[0], drop=True, inplace=True)
    df.to_csv(csv_outpath)
    print("Exported to", csv_outpath)


if __name__ == "__main__":
    main()     
