import pandas as pd

def process_data(df):
    # 1. Convert to Datetime first (this allows the .dt accessor)
    df['camp_date_dt'] = pd.to_datetime(df['camp_date'], format='%m-%d-%y', errors='coerce')

    # 2. Extract the Year while it is still a Datetime object
    # df['Year'] = df['camp_date_dt'].dt.year.fillna(0).astype(int)
    df['Year'] = df['camp_date_dt'].dt.year.astype('Int64')

    # 3. NOW convert the column to a date-only format for display
    df['camp_date_dt'] = df['camp_date_dt'].dt.date
    
    return df