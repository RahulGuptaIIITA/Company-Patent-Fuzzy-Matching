import pandas as pd
import numpy as np
import datetime

from constants import (DEFAULT_END_DATE,
                       VENTURE_EXPERT_DATA_DUMP_PATH)

def read_venture_expert_data(csv_path):
   """
   Converting the dataframe to csv
   """
   return pd.read_csv(csv_path)

def update_venture_start_date(venture_df):
   """
   Start date popullated using the following algorithm.
       i. If the Company Funding date is present, then start_date = funding_date - 365 days
       ii. If the company funding date not present, then it is populated using 
           the first_investment date - 5 years
   """
   # Start date using funding date column
   venture_df['start_date_funding'] = pd.to_datetime(venture_df['Company\nFounding\nDate'], errors='coerce')
   venture_df['start_date_funding'] = venture_df['start_date_funding'] - datetime.timedelta(days = 3650)

   # Start date using first recieved investment date
   venture_df['start_date_investment'] = pd.to_datetime(venture_df['Date Company\nReceived First\nInvestment'], errors='coerce')
   venture_df['start_date_investment'] = venture_df['start_date_investment'] - datetime.timedelta(days = 3650)

   # Using the investment date only when the funding date is not available
   venture_df['start_date'] = venture_df['start_date_funding'].fillna(venture_df['start_date_investment'])
   venture_df['start_date'] = pd.DatetimeIndex(venture_df['start_date']).year
   return venture_df

def update_venture_end_date(venture_df, default_end_date = DEFAULT_END_DATE):
   """
   Using the Company current situation date for populating end_date.
   If the company_current situation date is present, use that as end date.
   Else todays date is considered as end date
   """
   default_date = datetime.datetime.strptime(default_end_date,"%m/%d/%Y")
   venture_df['end_date'] = pd.to_datetime(venture_df['Company Current\nSituation Date'], errors='coerce')
   venture_df['end_date'] = venture_df['end_date'].fillna(default_date).dt.date
   venture_df['end_date'] = pd.DatetimeIndex(venture_df['end_date']).year
   return venture_df

def normalizing_venture_data(venture_df):
   venture_df['company_name'] = venture_df['Company Name'].str.upper()
   venture_df['vxfirm_id'] = venture_df['VXFirm_ID']
   final_venture_df = venture_df[['vxfirm_id','company_name', 'start_date', 'end_date']]
   return final_venture_df

def parse_venture_data():
   venture_df = read_venture_expert_data(VENTURE_EXPERT_DATA_DUMP_PATH)
   venture_df = update_venture_start_date(venture_df)
   venture_df = update_venture_end_date(venture_df)
   final_venture_df = normalizing_venture_data(venture_df)
   return final_venture_df

def save_parsed_venture_data(venture_df, venture_pkl_path):
   venture_df.to_pickle(venture_pkl_path)

def load_venture_pkl(venture_pkl_path):
   return pd.read_pickle(venture_pkl_path)
