import pandas as pd
from src.preferences import summarize_preferences

def test_preference_summary():
    out=summarize_preferences(pd.DataFrame({'cuisines':['Indian, Chinese','Indian'], 'rating':[4.0,3.5]}))
    assert out['rows']==2
    assert out['top_cuisines']['Indian']==2
