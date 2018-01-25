# Fuzzy Matching
Fuzzy matching for Patent to company mapping


1. Download the PatentData4_Sunil_V1.txt and VentureExpertData.csv data files
https://drive.google.com/open?id=18s9WwnuoFJQfEYG9Z51BR2B2eF79C5Gj

2. Add these files into RA_Patent_Mapping/data/ folder

3. If you are doing a new run, then delete the data/logging and data/cache folder

4. Make necessary changes in the configuration file.
	./RA_Patent_Mapping/data/configuration.txt

5. Run the following scripts to map the venture expert data to patent data with probability match.
	1.patent_venture_mapping.py
	python ./RA_Patent_Mapping/src/python/patent_venture_mapping.py

	The output is written to the following file.
		./RA_Patent_Mapping/logging/equivalence_output.txt

6. For the post process, run the following script
	This script will provide all necessary columns for modelling and provides all necessary constraints.

	The final output is available in the following file
		./RA_Patent_Mapping/logging/processed_equivalence_output.txt

 
