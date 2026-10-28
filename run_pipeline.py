import argparse, json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from src.config import OUTPUTS
from src.data import load_visits, load_zomato
from src.forecasting import evaluate_forecasts
from src.preferences import summarize_preferences

def main():
    p=argparse.ArgumentParser(); p.add_argument('--use-sample',action='store_true'); args=p.parse_args()
    OUTPUTS.mkdir(exist_ok=True)
    if args.use_sample:
        print('Sample mode is only a software test; do not submit its results.')
        dates=pd.date_range('2024-01-01',periods=180)
        visits=pd.DataFrame({'visit_date':dates,'visitors':[100+20*((d.dayofweek)%7)+i%9 for i,d in enumerate(dates)]})
        metrics,preds=evaluate_forecasts(visits)
        pref={'note':'Synthetic software-test data only; not real findings.'}
    else:
        visits=load_visits(); metrics,preds=evaluate_forecasts(visits)
        try: pref=summarize_preferences(load_zomato())
        except FileNotFoundError as e: pref={'warning':str(e)}
    metrics.to_csv(OUTPUTS/'forecast_metrics.csv',index=False)
    preds.to_csv(OUTPUTS/'forecast_predictions.csv',index=False)
    (OUTPUTS/'preference_summary.json').write_text(json.dumps(pref,indent=2,default=str),encoding='utf-8')
    fig,ax=plt.subplots(figsize=(11,5)); ax.plot(preds.visit_date,preds.visitors,label='Actual'); ax.plot(preds.visit_date,preds.baseline,label='Seasonal naive'); ax.plot(preds.visit_date,preds.random_forest,label='Random Forest'); ax.set(title='Daily visitor forecast: chronological holdout',xlabel='Date',ylabel='Total visitors'); ax.legend(); fig.tight_layout(); fig.savefig(OUTPUTS/'forecast_comparison.png',dpi=180); plt.close(fig)
    print(metrics.to_string(index=False)); print('Outputs saved to',OUTPUTS)
if __name__=='__main__': main()
