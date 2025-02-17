import pandas as pd

def map_npd(df):
    """
    this function map npd plays to their region (north, norwegian, or barent sea)

    """
    # Create a copy of the input DataFrame to avoid modifying the original data.
    df_info = df.copy()

    # Convert string values to lowercase in the specified columns.
    df_info['result NPD play'] = df_info['result NPD play'].apply(
        lambda x: x.lower() if isinstance(x, str) else x
    )
    df_info['prognosis NPD play'] = df_info['prognosis NPD play'].apply(
        lambda x: x.lower() if isinstance(x, str) else x
    )

    # Reset the index and drop the old index.
    df_info.reset_index(drop=True, inplace=True)

    # Define the lists of plays corresponding to each region.
    north_sea = [
        'neo/frigg-1', 'neo/grid-1', 'nol-1', 'npc-1', 'npc-2', 'npc-3', 'npc-4', 'npc-5',
        'nsbku-1', 'nkl-2', 'nku-2', 'nku-3', 'nku-4', 'nku-5', 'nju-1', 'nju-2', 'nju-3',
        'njl,jm-1', 'njl,jm-2', 'njl,jm-3', 'njl,jm-4', 'njl,jm-5', 'njm-1', 'nru,jm-1',
        'npl-1', 'npl-2', 'nkl-x', 'nku-x', 'nmi-1', 'nju-'
    ]
    
    norwegian_sea = [
        'nhjj-x', 'nhru-x', 'nheo-x', 'nhplei-1', 'nhpc-1', 'nhpc-2', 'nhpc-4', 'nhku-2',
        'nhku-3', 'nhku-4', 'nhku-5', 'nhku-6', 'nhkl-2', 'nhkl-3', 'nhju-1', 'nhju-2',
        'nhjm-1', 'nhjl,jm-1', 'nhjl,jm-2', 'nhjl,jm-3', 'nhpp,rr-1', 'nhpe-x', 'hju-1'
    ]
    
    barents_sea = [
        'beo-1', 'bpc-1', 'bju,kl-3', 'bku-x', 'bjl,jm-5', 'bjl,jm-6', 'bjl,jm-7', 'brl,rm-4',
        'brl,rm-5', 'brl-1', 'bru-1', 'bru-2', 'bpm,pu-4', 'bpm,pu-5', 'bpm,pu-7', 'bpu-4',
        'bcu,pl-3', 'bcu,pl-4', 'bcu,pp-4', 'bcu,pp-5', 'bcu,pp-7', 'bcl-3', 'bcl-4',
        'bpu-x', 'bpl-x'
    ]

    # Helper function to map a play value to its region.
    def map_region(value):
        if isinstance(value, str):
            if value in north_sea:
                return 'north sea'
            elif value in norwegian_sea:
                return 'norwegian sea'
            elif value in barents_sea:
                return 'barents sea'
        return value

    # Apply the mapping to both 'result NPD play' and 'prognosis NPD play' columns.
    df_info['result NPD play'] = df_info['result NPD play'].apply(map_region)
    df_info['prognosis NPD play'] = df_info['prognosis NPD play'].apply(map_region)

    return df_info

