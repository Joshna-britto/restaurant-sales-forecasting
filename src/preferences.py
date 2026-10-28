import pandas as pd

def summarize_preferences(df):
    result={'rows':int(len(df)),'columns':list(map(str,df.columns))}
    for col in df.columns:
        if any(k in str(col).lower() for k in ['cuisine','listed_in']):
            values=df[col].dropna().astype(str).str.split(',').explode().str.strip()
            result['top_cuisines']=values.value_counts().head(10).to_dict(); break
    rating=next((c for c in df.columns if 'rate' in str(c).lower() or 'rating' in str(c).lower()),None)
    if rating: result['rating_column']=str(rating); result['rating_non_null']=int(df[rating].notna().sum())
    return result
