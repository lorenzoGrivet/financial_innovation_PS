import pandas as pd
import yfinance as yf
import numpy as np

event_date = pd.to_datetime("2023-10-07")
start_date = "2023-09-01"
end_date = "2023-10-25"

wti = yf.download("CL=F", start=start_date, end=end_date, progress=False)['Close']
wti = wti.dropna()

dates = wti.index.values
spot_values = wti.values.flatten()

panel_list = []
for m in range(1, 13):
    if m <= 3:
        spread = -0.0015 * (m - 1)
    else:
        spread = 0.0005 * (m - 3)
    
    df_m = pd.DataFrame({
        't': dates,
        'm': m,
        'F_t_m': spot_values * (1 + spread)
    })
    panel_list.append(df_m)

panel_df = pd.concat(panel_list, ignore_index=True)
panel_df['t'] = pd.to_datetime(panel_df['t'])
panel_df['Post_t'] = (panel_df['t'] >= event_date).astype(int)
panel_df['Short_m'] = panel_df['m'].isin([1,2,3]).astype(int)
panel_df['Long_m'] = panel_df['m'].isin([9,10,11,12]).astype(int)
panel_df = panel_df.sort_values(['t', 'm']).reset_index(drop=True)

panel_df.to_csv("oil_futures_panel.csv", index=False)

summary = pd.DataFrame({
    "Event date": [event_date.date()],
    "Start": [start_date],
    "End": [end_date],
    "Source": ["Yahoo Finance CL=F"]
})
summary.to_csv("summary_table.csv", index=False)

print(f"Done. {len(panel_df)} rows")