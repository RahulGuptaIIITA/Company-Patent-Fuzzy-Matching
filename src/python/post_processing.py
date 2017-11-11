import pandas as pd
from constants import (VENTURE_EXPERT_PKL_PATH,
                       PATENT_PKL_PATH,
                       EQUIVALENCE_OUTPUT_PATH,
                       VENTURE_EXPERT_PROCESSED_IDS,
                       PROCESSED_EQUIVALENCE_OUTPUT_PATH,
                       CONFIGURATION_PATH)
from parse_venture_expert import (parse_venture_data,
                                  save_parsed_venture_data,
                                  load_venture_pkl)
from parse_patent import (parse_patent_data,
                          save_parsed_patend_data,
                          load_patend_pkl)
import json

def read_configuration_file():
    """
    Reading the configuration file
    """
    with open(CONFIGURATION_PATH) as fp:
        config = json.loads(fp.read())
    return config

config = read_configuration_file()
PROBABILITY_RANKING_THRESHOLD = config['probability_ranking_threshold']
PREFIX_LENGTH = config['prefix_length']
IS_HARD_PREFIX = config['is_hard_prefix']
NUM_PATENT_TO_VX_FILTER = config['num_patent_to_vx_filter']

#ALLOWED_NUM_COMPANIES = 10

def read_file(file_path):
    """
    Read the equivalence output file
    """
    data_dict = {"vxfirm_id":[], "pnum":[], "vx_company_name":[], "vx_normalized_company_name":[], 
                "pat_nomralized_company":[], "rank":[], "prefix_len_fix": [], "venture_start_date":[]}
    with open(file_path) as fp:
        for line in fp.readlines():
            row = line.split("|")
            data_dict["vxfirm_id"].append(row[0])
            data_dict["pnum"].append(row[1])
            data_dict["vx_company_name"].append(row[2])
            data_dict["vx_normalized_company_name"].append(row[3])
            data_dict["pat_nomralized_company"].append(row[4])
            data_dict["rank"].append(row[5])
            data_dict["prefix_len_fix"].append(row[6])
            data_dict["venture_start_date"].append(row[7])
    return pd.DataFrame.from_dict(data_dict)

def patent_to_company_filter(df):
    """
    This implies that for 1 patent can have mapping to n venture company data set.
    This is controlled in the configuration file.
    """
    df['patent_ranking'] = df.sort_values(['rank'], ascending=[False]) \
             .groupby(['pnum']) \
             .cumcount() + 1
    df = df[df['patent_ranking'] <= NUM_PATENT_TO_VX_FILTER]
    return df

def threshold_filter(df, rank_threshold):
    """
    One can put threshold filter as 0.7, 0.8 matching
    """
    df = df[df['rank'] >= rank_threshold]
    return df

def vx_company_ranking(df):
    """
    Initially wrote this code to make use of the constarint that, 
    one patent can belong to one company and filtering on all the other 
    patents that are mapped to many venture expert data. Keeping the highest 
    ranking. But this was not necessary, since Prof. want this to be looked by 
    RA and do the mapping.
    """
    df['rank_str'] = df['rank'].astype(str)
    """
    df['vx_company_ranking'] = df.sort_values(['rank'], ascending=[False]) \
            .groupby(['vxfirm_id', 'company_name']) \
            .cumcount() + 1
    df['vx_ranking'] = df.sort_values(['rank'], ascending=[False]) \
            .groupby(['vxfirm_id', 'vx_company_ranking']) \
            .cumcount() + 1
    """    
    df['rank_company_str'] = df['rank_str'] + df['pat_company_name']
    df['vx_company_rank'] = df.sort_values(['vxfirm_id', 'rank'], ascending=[True, False])\
            .groupby(['vxfirm_id'])['rank_company_str'].rank(method='dense', ascending=False)

    #df = df[(df.vx_company_rank <= ALLOWED_NUM_COMPANIES)]
    df.drop(['rank_str', 'rank_company_str'], axis=1, inplace=True)
    return df

def soft_hard_prefix_constraint(df, is_hard_prefix, prefix_len):
    """
    Based on the hard or soft constraint, this function is used.
    In soft-constraint --> The constraint used is from the mapping logic 7 or 5 or 3 prefix match.
    In hard-constraint --> The first few words must be same to qualify.
    """
    if not is_hard_prefix:
        return df[df.prefix_len_fix >= prefix_len]
    else:
        return df[df.vx_normalized_company_name.str.slice(0, prefix_len) ==\
                  df.pat_nomralized_company.str.slice(0, prefix_len)]

def constraints_on_output(df):
    """
    All the above explained constraints are called in this function
    """
    df = soft_hard_prefix_constraint(df, IS_HARD_PREFIX, PREFIX_LENGTH)
    df = patent_to_company_filter(df)
    df = threshold_filter(df, PROBABILITY_RANKING_THRESHOLD)
    df = vx_company_ranking(df)
    #df = df.sort_values(['vxfirm_id', 'rank', 'vx_company_rank'], ascending=[True, False, False])
    df = df.sort_values(['pnum', 'patent_ranking'], ascending=[True, True])
    return df

def clean_dataframe(df):
    """
    Data cleaning from the output file. Renaming of the column names, 
    creating key for faster lookup.
    """
    df = df[["vxfirm_id", "pnum", "vx_company_name", "company_name", 
             "vx_normalized_company_name", "pat_nomralized_company", "rank", 
             "prefix_len_fix", "venture_start_date", "ayear"]]
    df.vxfirm_id = df.vxfirm_id.astype(int)
    df.pnum = df.pnum.astype(int)
    df['rank'] = df['rank'].astype(float)
    df.prefix_len_fix = df.prefix_len_fix.astype(int)
    
    df.venture_start_date = df.venture_start_date.str.strip(r'\\n')
    df.venture_start_date = df.venture_start_date.astype(int)
    df.venture_start_date = pd.to_numeric(df.venture_start_date, errors='coerce')
    df["is_valid_funding_date"] = df.ayear >= df.venture_start_date
    df = df.rename(columns={'company_name': 'pat_company_name'})
    return df

def main():
    """
    1. Reads the output file generated by equivalence search algorithm
    2. Appends few extra columns like normalized company names, year etc.
    3. Puts all the constraints like 1 VX company can have 300 expert venture company max
    4. Also hard constraint or soft constraint can be controlled on the output version of 
        equivalence algorithm.
    """
    output_df = read_file(EQUIVALENCE_OUTPUT_PATH)
    patent_df = load_patend_pkl(PATENT_PKL_PATH)
    merge_df = pd.merge(output_df, patent_df, on="pnum")

    cleaned_df = clean_dataframe(merge_df)
    final_output_df = constraints_on_output(cleaned_df)
    final_output_df.to_csv(PROCESSED_EQUIVALENCE_OUTPUT_PATH, sep="|", index=False)

if __name__ == "__main__":
    main()