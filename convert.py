import pandas as pd

CSV_PATH = './funding_data.csv'
JSON_PATH = './funding_data.json'
PARQUET_PATH = './funding_data.parquet'

def _load_data(inpath=CSV_PATH):
    df = pd.read_csv(inpath)
    print(f"Loaded {inpath}' with {len(df)} rows")
    df.rename(columns={
        'oso_slug': 'project_name',
        'project_name': 'display_name' 
    }, inplace=True)
    return df


def to_json(inpath=CSV_PATH, outpath=JSON_PATH):
    df = _load_data(inpath)
    df.to_json(outpath, orient='records', indent=2)
    print(f'Converted {inpath} to {outpath}')


def to_parquet(inpath=CSV_PATH, outpath=PARQUET_PATH):
    df = _load_data(inpath)
    df.to_parquet(outpath)
    print(f'Converted {inpath} to {outpath}')


if __name__ == '__main__':
    to_json()
    to_parquet()