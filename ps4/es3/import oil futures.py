# import yfinance as yf
# import pandas as pd

# # 1. Define the 12 active tickers starting from May 2026
# # These represent maturities m=1 through m=12
# # tickers = [
# #     "BZK26.NYM", # m=1  (May 2026)
# #     "BZM26.NYM", # m=2  (Jun 2026)
# #     "BZN26.NYM", # m=3  (Jul 2026)
# #     "BZQ26.NYM", # m=4  (Aug 2026)
# #     "BZU26.NYM", # m=5  (Sep 2026)
# #     "BZV26.NYM", # m=6  (Oct 2026)
# #     "BZX26.NYM", # m=7  (Nov 2026)
# #     "BZZ26.NYM", # m=8  (Dec 2026)
# #     "BZF27.NYM", # m=9  (Jan 2027)
# #     "BZG27.NYM", # m=10 (Feb 2027)
# #     "BZH27.NYM", # m=11 (Mar 2027)
# #     "BZJ27.NYM"  # m=12 (Apr 2027)
# # ]
# tickers = [
#     "BZV23.NYM", # Oct 2023
#     "BZX23.NYM", # Nov 2023
#     "BZZ23.NYM", # Dec 2023
#     "BZF24.NYM", # Jan 2024
#     "BZG24.NYM", # Feb 2024
#     "BZH24.NYM", # Mar 2024
#     "BZJ24.NYM", # Apr 2024
#     "BZK24.NYM", # May 2024
#     "BZM24.NYM", # Jun 2024
#     "BZN24.NYM", # Jul 2024
#     "BZQ24.NYM", # Aug 2024
#     "BZU24.NYM"  # Sep 2024
# ]

# # Map each ticker to its exact maturity index (1 to 12)
# maturity_map = {ticker: i+1 for i, ticker in enumerate(tickers)}

# # 2. Define our 2-month window and the "Shock" Event Date
# event_date = pd.to_datetime("2023-10-07")

# start_date = "2023-09-01"
# end_date   = "2023-10-25"

# # 3. Download the data from Yahoo Finance
# print(f"Downloading data from {start_date} to {end_date}...")
# # We extract just the 'Close' prices (daily settlement prices)
# raw_data = yf.download(tickers, start=start_date, end=end_date)['Close']

# # 4. Reshape the data from "Wide" to "Long" (Panel format)
# # Move the Date index into a standard column
# df = raw_data.reset_index()

# # Melt the dataframe
# panel_df = df.melt(
#     id_vars=['Date'], 
#     value_vars=tickers,
#     var_name='Contract', 
#     value_name='F_t_m'
# )

# # 5. Build the required variables for the exercise
# # Rename Date to 't'
# panel_df.rename(columns={'Date': 't'}, inplace=True)

# # Assign the maturity index 'm'
# panel_df['m'] = panel_df['Contract'].map(maturity_map)

# # Drop any weekends or holidays where the market was closed
# panel_df = panel_df.dropna().sort_values(by=['t', 'm']).reset_index(drop=True)

# # Create the indicator (dummy) variables requested in the exercise prompt
# panel_df['Post_t'] = (panel_df['t'] >= event_date).astype(int)
# panel_df['Short_m'] = panel_df['m'].isin([1, 2, 3]).astype(int)
# panel_df['Long_m'] = panel_df['m'].isin([9, 10, 11, 12]).astype(int)

# # 6. Final Cleanup and Formatting
# final_columns = ['t', 'Contract', 'm', 'F_t_m', 'Post_t', 'Short_m', 'Long_m']
# panel_df = panel_df[final_columns]

# # Print the results
# print("\nPanel Dataset Successfully Built!")
# print(f"Total observations: {len(panel_df)}")
# print("\nFirst 12 rows (The curve for the first available trading day):")
# print(panel_df.head(12))

# # Optional: Save to CSV so you don't have to run the download again
# panel_df.to_csv("oil_futures_panel.csv", index=False)

# # =========================
# # 7. SUMMARY TABLE (richiesta)
# # =========================
# summary_table = pd.DataFrame({
#     "Event date": [event_date.date()],
#     "Start date": [start_date],
#     "End date": [end_date],
#     "Source": ["Yahoo Finance (yfinance)"]
# })

# print("\n=== SUMMARY TABLE ===")
# print(summary_table)
# summary_table.to_csv("summary_table.csv", index=False)

############################################################################################################