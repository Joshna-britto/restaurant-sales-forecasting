import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

def evaluate_forecasts(df):
    daily = df.groupby('visit_date', as_index=False)['visitors'].sum().sort_values('visit_date')
    if len(daily) < 40: raise ValueError('Need at least 40 daily observations for a meaningful chronological split.')
    daily['dow'] = daily.visit_date.dt.dayofweek
    daily['month'] = daily.visit_date.dt.month
    daily['dayofyear'] = daily.visit_date.dt.dayofyear
    for lag in (1,7,14,28): daily[f'lag_{lag}'] = daily.visitors.shift(lag)
    daily = daily.dropna().reset_index(drop=True)
    split = int(len(daily)*0.8)
    train, test = daily.iloc[:split].copy(), daily.iloc[split:].copy()
    features = ['dow','month','dayofyear','lag_1','lag_7','lag_14','lag_28']
    pred_base = test['lag_7'].to_numpy()
    model = RandomForestRegressor(n_estimators=250, random_state=42, min_samples_leaf=2, n_jobs=-1)
    model.fit(train[features], train.visitors)
    pred_rf = model.predict(test[features])
    rows=[]
    for name,pred in [('Seasonal naive (lag 7)',pred_base),('Random Forest',pred_rf)]:
        mae=mean_absolute_error(test.visitors,pred); rmse=mean_squared_error(test.visitors,pred)**0.5
        denom=np.abs(test.visitors.to_numpy())+np.abs(pred)
        smape=float(np.mean(np.where(denom==0,0,2*np.abs(test.visitors.to_numpy()-pred)/denom))*100)
        rows.append({'model':name,'MAE':mae,'RMSE':rmse,'sMAPE_percent':smape})
    return pd.DataFrame(rows), test[['visit_date','visitors']].assign(baseline=pred_base, random_forest=pred_rf)
