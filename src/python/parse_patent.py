
import pandas as pd
import numpy as np

from constants import (PATENT_DATA_FILE,
                       REQUIRED_PATENT_HEADERS,
                       FILTER_ASSIGNED_GROUP_BFH_2017_DATA)

def lazy_read_file(file_path):
	"""
	Load to memory only when required line by line
	"""
	with open(file_path, "r") as fp:
		for i in fp:
			yield i

def assign_headers(col_data):
	"""
	Fetching only the required headers from the txt file
	"""
	header_dict = dict()
	data = dict()
	for idx, col in enumerate(col_data):
		if col in REQUIRED_PATENT_HEADERS:
			header_dict[col] = idx
			data[col] = list()
	return header_dict, data

def parse_data(file_path):
	"""
	Parse the txt and convert to a dictionary
	"""
	data = dict()
	header_dict = dict()
	patent_data = lazy_read_file(file_path)
	for line in patent_data:
		col_data = line.split("\t")
		if not header_dict:
			header_dict, data = assign_headers(col_data)
			if len(header_dict) != len(REQUIRED_PATENT_HEADERS):
				raise Exception("The default column name and patent header names do not match")
			continue
		for col, idx in header_dict.items():
			data[col].append(col_data[idx])
	return data

def filter_ass_group_data(df):
	"""
	Remove all the unnecessary categories, like Individual etc.
	"""
	df = df[~df.patassg_group_bfh_2017.isin(FILTER_ASSIGNED_GROUP_BFH_2017_DATA)]
	return df

def normalize_patent_data(raw_patent_df):
	"""
	1. Remove unnecessary category like individuals from patassg_group_bfh_2017
	2. Covert date to year
	3. Drop unnecessary columns
	"""
	patent_df = filter_ass_group_data(raw_patent_df)
	patent_df['company_name'] = patent_df['firstassignee'].str.upper()
	patent_df['ayear'] = patent_df['ayear'].astype('int')
	patent_df.drop('firstassignee', 1, inplace=True)
	return patent_df

def parse_patent_data():
	"""
	1. Read the patent dump as pandas dataframe.
	2. Normalize the dataframe
	"""
	raw_patent_df = pd.DataFrame(parse_data(PATENT_DATA_FILE))
	patent_df = normalize_patent_data(raw_patent_df)
	return patent_df

def save_parsed_patend_data(patent_df, patent_pkl_path):
	"""
	Save the normalized dataframe as pickel file
	"""
	patent_df.to_pickle(patent_pkl_path)

def load_patend_pkl(patent_pkl_path):
	"""
	Load the normalized dataframe from pickel file to memory
	"""
	return pd.read_pickle(patent_pkl_path)
