from parse_patent import (parse_patent_data,
                          save_parsed_patend_data,
                          load_patend_pkl)
from parse_venture_expert import (parse_venture_data,
                                  save_parsed_venture_data,
                                  load_venture_pkl)
from company_info_trie import (possible_company_search,
                                          normalize_words)

import pandas as pd
import numpy as np
from constants import (VENTURE_EXPERT_PKL_PATH,
                       PATENT_PKL_PATH,
                       EQUIVALENCE_OUTPUT_PATH,
                       VENTURE_EXPERT_PROCESSED_IDS)
import os

def create_patent_venture_pkl():
    """
    Convert patent & venture raw data into pandas dataframe format 
    and save it as a pickel file.
    """
    patent_df = parse_patent_data()
    venture_df = parse_venture_data()
    save_parsed_patend_data(patent_df, PATENT_PKL_PATH)
    save_parsed_venture_data(venture_df, VENTURE_EXPERT_PKL_PATH)

def exact_match():
    """
    This gives those mapping with exact match between patent and venture data
    """
    patent_df = load_patend_pkl(PATENT_PKL_PATH)
    venture_df = load_venture_pkl(VENTURE_EXPERT_PKL_PATH)
    merge_df = pd.merge(venture_df, patent_df, on="company_name")
    merge_df = merge_df[(merge_df['ayear']>=merge_df['start_date']) &\
                        (merge_df['ayear']<=merge_df['end_date'])]
    return merge_df

def write_to_file(file_path, data):
    """
    Function to write the output to a file
    """
    with open(file_path, "a") as fp:
        for row in data:
            fp.write('|'.join(row) + "\n")

def write_venture_expert_pids(filepath, data):
    """
    Function to write pids to the file so that on re-run it 
    starts from where the algorithm had stopped. To maintain the state of
    the previous run
    """
    with open(filepath, "a") as fp:
        fp.write(str(data)+"\n")

def read_venture_expert_processed_ids(filepath):
    """
    Reading the venture expert process id if exists, so that it 
    can continue from the previous stop
    """
    if not os.path.exists(filepath):
        return []
    with open(filepath) as fp:
        lines = fp.read().splitlines()
    return lines

"""
def get_patent_detail(patent_df, patent_id):
    row_info = patent_df[patent_df.index == patent_id]
    pat_company_name = str(row_info.iloc[0].company_name)
    pat_year = row_info.iloc[0].ayear
    return pat_company_name, pat_year
"""

def equivalence_match():
    """
    Finds all the matching company names using equivalence and similarity search algorithm.

    1. Loads venture expert pkl file to memeory.
    2. Iterates for each row in the venture expert data.
    3. If the process_id is already parsed (In the process_id text file) then skips
    4. From the equivalence search algorithm finds the matching patent company name 
    5. Writes the output to the file.
    """
    venture_df = load_venture_pkl(VENTURE_EXPERT_PKL_PATH)
    venture_ids_processed = read_venture_expert_processed_ids(VENTURE_EXPERT_PROCESSED_IDS)

    #patent_df = load_venture_pkl(PATENT_PKL_PATH)
    #patent_df = patent_df.set_index('pnum')

    processed_ids = {int(val): True for val in venture_ids_processed}
    for row in venture_df.itertuples():
        print("Processing venture expert id: "+ str(row.vxfirm_id))
        
        if row.vxfirm_id in processed_ids:
            continue
        
        mapped_result = possible_company_search(row.company_name)
        if mapped_result:
            write_data = list()
            for map_data in mapped_result:
                pat_id, pat_nomralized_company, rank, prefix_len_fix = map_data[0], map_data[1], map_data[2], map_data[3]

                #pat_company_name, pat_year = get_patent_detail(patent_df, pat_id)
                #is_valid_funding_date = False if pat_year < row.start_date else True

                vx_normalized_company_name = normalize_words(str(row.company_name))

                """
                write_data.append([str(row.vxfirm_id), str(pat_id), str(row.company_name),
                    str(pat_company_name), str(vx_normalized_company_name),
                    str(pat_nomralized_company), str(rank), str(prefix_len_fix),
                    str(row.start_date), str(pat_year), str(is_valid_funding_date)])
                """
                write_data.append([str(row.vxfirm_id), str(pat_id), str(row.company_name),
                    str(vx_normalized_company_name), str(pat_nomralized_company), str(rank), str(prefix_len_fix),
                    str(row.start_date)])
                

            write_to_file(EQUIVALENCE_OUTPUT_PATH, write_data)
        write_venture_expert_pids(VENTURE_EXPERT_PROCESSED_IDS, row.vxfirm_id)

def main():
    # To run fuzzy search
    create_patent_venture_pkl()
    equivalence_match()

    # To run exact matching
    #create_patent_venture_pkl()
    #merge_df = exact_match()
    #print(merge_df)

if __name__ == "__main__":
    main()