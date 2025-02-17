# PoS-verification---NCS
Probability Forecast Verification in Petroleum Exploration: Insights from the Norwegian Continental Shelf

To investigate the quality of forecasts on geological success rates as well as reservoir, source, and trap, we use a combination of attribute diagram and verification measures such as brier score, skill score, and bias score.
Therefore, these codes are aimed to read the dataset of exploration activities of companies active on the Norwegian Continental Shelf (NCS), clean it and generate attribute diagrams, probability verification measures, and the main reasons for exploration failure (dry wells) across the three major exploration areas on the NCS (North Sea, the Norwegian Sea, and the Barents Sea). 
The original dataset includes pre-drill forecasts and post-drill results of prospects. Before drilling any well, a company must report its forecast of technical success (PoS) and the factors used in the PoS calculation to the NOD. Within six months of completing the drilling of the well, or after conducting standard post-drilling analysis, the company must submit a post-drill report to the NOD specifying whether the well was a discovery and, if it was not, which underlying factors used in the PoS calculation were failures. From the dataset, we extract only the probabilities and event outcomes, as it contains various other details about the prospects.


Here you can see how to use the codes to generate attribute diagrams and verification measures:
# Attribute diagram for all data:
     
  ### 1- Download the dataset from the following link:
    https://factpages.sodir.no/en/wellbore/Miscellaneous/PrognosisResults
  
  ### 2- Read the dataset in python and use it as the input to data_cleaning.py. The output will be a dataframe.
  ### 3- Use the dataframe in step 2 to generate plots as follows: 
    import pandas as pd
    import  data_cleaning
    import attribute_subplots
    
    data = pd.read_excel('PrognosisResultData_Released.xlsx')
    df = data_cleaning.data_reshape(data)

    use your desired year period
    years = [1990, 2022]
    attribute_subplots.attribute_diagram(df, years)
  
# Attribute diagram for NPD regions:
  ### For NPD regions (North, Norwegian, and Barent sea), firstly we need to map plays to their region.

  ### 1 - Repeat step 1 and 2 as above.
  ### 2- Map the plays to their region using map_npd.py. The output will be a dataframe (df_npd).
  ### 3- Use the dataframe (df_npd) in step 2 to generate plots as follows:
  
    import map_npd
    import attribute_npd_subplots
    df_npd = map_npd.map_npd(df)

    use your desired year period
    years = [1990, 2022]
    attribute_npd_subplots.attribute_diagram(df_npd, years)
  
# 3. Main reasons for exploration failure across NPD regions
   
  ### 1 - Repeat step 1 as above.
  ### 2 - Read the dataset in python and use it as the input data_cleaning_no_replicate.py. The output will be a dataframe.
  ### 3- Map the plays to their region using map_npd.py. The output will be a dataframe (df_npd).
  ### 4 - Use post_drill_risk.py to generate	 the pie chart.

    import pandas as pd
    import  data_cleaning_no_replicate
    import map_npd
    import post_drill_risk
    
    data = pd.read_excel('PrognosisResultData_Released.xlsx')
    df = data_cleaning_no_replicate.data_reshape(data)
    df_npd = map_npd.map_npd(df)

    post_drill_risk.risk_pie_chart(df_npd)







