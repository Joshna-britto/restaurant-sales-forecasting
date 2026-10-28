import pandas as pd
from .config import RECRUIT

def load_visits():
    path = RECRUIT / 'air_visit_data.csv'
    if not path.exists():
        raise FileNotFoundError(f'Missing {path}. Download the Kaggle competition files and extract them there.')
    df = pd.read_csv(path)
    needed = {'air_store_id','visit_date','visitors'}
    if not needed.issubset(df.columns): raise ValueError(f'Expected columns: {sorted(needed)}')
    df['visit_date'] = pd.to_datetime(df['visit_date'], errors='coerce')
    df['visitors'] = pd.to_numeric(df['visitors'], errors='coerce')
    return df.dropna(subset=['visit_date','visitors']).sort_values('visit_date')

def load_zomato():
    files = list((RECRUIT.parent / 'zomato').glob('*.csv'))
    if not files: raise FileNotFoundError('Place one Zomato restaurant metadata CSV in data/raw/zomato/.')
    return pd.read_csv(files[0], low_memory=False)
