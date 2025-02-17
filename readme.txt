1- Download the dataset from the following link:
https://factpages.sodir.no/en/wellbore/Miscellaneous/PrognosisResults

2- Read the dataset in python and use it as the input to data_cleaning.py. The output will be a dataframe.

data = pd.read_excel('PrognosisResultData_Released.xlsx')

import  data_cleaning

df = data_cleaning.data_reshape(data)


3- Use the dataframe in step 2 to generate plots as follows:

import attribute_subplots

# use your desired year period
years = [1990, 2022]
attribute_subplots.attribute_diagram(df, years)


############################################################################################################################


For NPD regions (North, Norwegian, and Barent sea), firstly we need to map plays to their region.

1 - Repeat step 1 and 2 as above.

2- Map the plays to their region using map_npd.py. The output will be a dataframe (df_npd).

import map_npd

df_npd = map_npd.map_npd(df)


3- Use the dataframe (df_npd) in step 2 to generate plots as follows:

import attribute_npd_subplots

# use your desired year period
years = [1990, 2022]
attribute_npd_subplots.attribute_diagram(df_npd, years)

############################################################################################################################

For Main reasons for exploration failure across the North Sea, Norwegian Sea, and Barents Sea:

1 - Repeat step 1 as above.

2 - Read the dataset in python and use it as the input data_cleaning_no_replicate.py. The output will be a dataframe.

data = pd.read_excel('PrognosisResultData_Released.xlsx')

import  data_cleaning_no_replicate

df = data_cleaning_no_replicate.data_reshape(data)

3- Map the plays to their region using map_npd.py. The output will be a dataframe (df_npd).

import map_npd

df_npd = map_npd.map_npd(df)


4 - Use post_drill_risk.py to generate	 the pie chart.

import post_drill_risk

post_drill_risk.risk_pie_chart(df_npd)


