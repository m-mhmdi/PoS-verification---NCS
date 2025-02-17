#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from itertools import chain

def data_reshape(data):
    # dropping the first row
    data = data.drop(0)

    # Separate observed and prognosis data
    data_obs = data[data['Prognosis - Result'].str.upper() != 'PROGNOSIS']
    data_prog = data[data['Prognosis - Result'].str.upper() != 'RESULT']

    # Find common well IDs
    well_ids_common = np.intersect1d(pd.unique(data_obs['Well name']), pd.unique(data_prog['Well name']))

    # Initialize lists
    well_prospect_ids = []
    technical_probs, reservoir_probs, source_probs, trap_probs = [], [], [], []
    discovery, reservoir, source, trap, years = [], [], [], [], []
    npd_play_obs = []
    npd_play_prog = []

    # Process data
    for w in well_ids_common:
        wells_obs = data_obs[data_obs['Well name'] == w]
        wells_prog = data_prog[data_prog['Well name'] == w]
        prospect_ids = np.intersect1d(pd.unique(wells_obs['Prospect name']), pd.unique(wells_prog['Prospect name']))

        for p in prospect_ids:
            prospects_obs = wells_obs[wells_obs['Prospect name'] == p]
            prospects_prog = wells_prog[wells_prog['Prospect name'] == p]

            # well-prospect names
            well_prospect_ids.append([w, p])
            # Probabilities
            technical_probs.append(list(prospects_prog["Probability Technical Total"]))
            reservoir_probs.append(list(prospects_prog["Probability Techn Reservoir"]))
            source_probs.append(list(prospects_prog["Probability Techn Source"]))
            trap_probs.append(list(prospects_prog["Probability Techn Trap"]))

            # Discovery and geological factors
            discovery.append(list(prospects_obs["Discovery?"]))
            reservoir.append(list(prospects_obs["OK Reservoir?"]))
            source.append(list(prospects_obs["OK Source/ Charge?"]))
            trap.append(list(prospects_obs["OK Trap?"]))

            # Years
            years.append([int(str(d)[:4]) for d in prospects_obs['Completion date']])

            # NPD Plays
            npd_play_obs.append(list(prospects_obs["NPD Play"]))
            npd_play_prog.append(list(prospects_prog["NPD Play"]))


    # Convert categorical data to binary
    def convert_to_binary(lst, mapping):
        for sublist in lst:
            if isinstance(sublist[0], str):
                sublist[0] = mapping.get(sublist[0].upper(), sublist[0])

    mapping = {'YES': 1, 'NO': 0, 'OK': 1, 'FAIL': 0}
    for lst in [discovery, reservoir, source, trap]:
        convert_to_binary(lst, mapping)

    # Handle multiple prognoses by duplicating observed data
    multi_prognosis_indices = [i for i, x in enumerate(technical_probs) if len(x) > 1]
    for idx in reversed(multi_prognosis_indices):
        for _ in range(len(technical_probs[idx]) - 1):
            well_prospect_ids.insert(idx, well_prospect_ids[idx])
            discovery.insert(idx, discovery[idx])
            reservoir.insert(idx, reservoir[idx])
            source.insert(idx, source[idx])
            trap.insert(idx, trap[idx])
            years.insert(idx, years[idx])
            npd_play_obs.insert(idx, npd_play_obs[idx])

    # Flatten lists
    flatten = lambda lst: list(chain.from_iterable(lst))
    dict_total = {
        'well_prospect': well_prospect_ids,
        'year': flatten(years),
        'result NPD play':flatten(npd_play_obs),
        'prognosis NPD play':flatten(npd_play_prog),
        'Technical Probability': flatten(technical_probs),
        'Reservoir Probability': flatten(reservoir_probs),
        'Source Probability': flatten(source_probs),
        'Trap Probability': flatten(trap_probs),
        'discovery?': flatten(discovery),
        'reservoir?': flatten(reservoir),
        'source?': flatten(source),
        'trap?': flatten(trap)
    }

    df = pd.DataFrame(dict_total)

    # Clean up placeholders
    def clean_placeholders(row):
        if row['discovery?'] == 1:
            for col in ['reservoir?', 'source?', 'trap?']:
                if pd.isna(row[col]):
                    row[col] = 1
        return row

    df = df.apply(clean_placeholders, axis=1)

    # Remove invalid data
    df = df[df[['Technical Probability', 'Reservoir Probability', 'Source Probability', 'Trap Probability']].notna().all(axis=1)]
    df = df[df[['reservoir?', 'source?', 'trap?', 'discovery?']].isin([0, 1]).all(axis=1)]

    # Reset index
    df = df.reset_index(drop=True)
    len(df)
    return df
    

