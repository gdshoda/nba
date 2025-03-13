

def download_injury_pdf():
    import requests
    # URL of the hosted PDF
    pdf_url = "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2024-11-08_12AM.pdf"

    # Download the PDF
    response = requests.get(pdf_url)
    response.raise_for_status()

    pdf_path = "temp.pdf"

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    return pdf_path


def get_nba_injury_pdf_data(pdf_path):
    import pandas as pd
    import numpy as np
    import camelot

    columns = ["119,199,264,424,585,666"]

    all_stream_tables = camelot.read_pdf(pdf_path, pages = 'all', flavor = 'stream', row_tol = 18, columns = columns)

    dfs = []

    for x in range(len(all_stream_tables)):
        table = all_stream_tables[x].df
        if x == 1:
            injury_report_datetime = table.iloc[0, 4]
            #print(datetime)
        table = table.iloc[1:]
        
        dfs.append(table)

    column_names = ["game_date", "game_start_time", "Matchup", "Team", "Player Name", "status", "reason"]

    concat_df = pd.concat(dfs, ignore_index = True)

    concat_df.columns = column_names

    concat_df['injury_report_datetime'] = injury_report_datetime

    concat_df[concat_df.select_dtypes(include=['object']).columns] = concat_df.select_dtypes(include=['object']).apply(lambda x: x.str.strip())

    concat_df.replace("", np.nan, inplace = True)

    concat_df.iloc[:, 0:6] = concat_df.iloc[:, 0:6].ffill()

    not_submitted_df = concat_df.loc[concat_df['reason'] == 'NOT YET SUBMITTED']

    not_submitted_df = not_submitted_df.copy()

    concat_df = concat_df.loc[concat_df['reason'] != 'NOT YET SUBMITTED']

    concat_df['game_date'] = pd.to_datetime(concat_df['game_date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')

    concat_df['game_start_time'] = concat_df['game_start_time'].str.replace(' (ET)', '')

    concat_df['injury_report_datetime'] = concat_df['injury_report_datetime'].str.replace("Injury Report: ", "")

    concat_df['injury_report_datetime'] = pd.to_datetime(concat_df['injury_report_datetime'], format = '%m/%d/%y %I:%M %p').dt.strftime('%Y-%m-%d %H:%M')

    concat_df = concat_df[['injury_report_datetime', 'game_date', 'Matchup', 'Team', 'Player Name', 'status', 'reason']]

    concat_df = concat_df.groupby(concat_df.columns[:-1].to_list(), as_index=False).agg({'reason': ' '.join})

    concat_df[['player_last_name','player_first_name']] = concat_df['Player Name'].str.split(",", expand = True)

    concat_df['player_name'] = concat_df['player_first_name'] + ' ' + concat_df['player_last_name']

    concat_df[['visitor_team_id', 'home_team_id']] = concat_df['Matchup'].str.split('@', expand = True)

    concat_df = concat_df[['injury_report_datetime', 'game_date', 'visitor_team_id', 'home_team_id', 'Team', 'player_name', 'player_first_name', 'player_last_name', 'status', 'reason']]

    not_submitted_df.loc[not_submitted_df['Player Name'] != np.nan, 'player_name'] = np.nan

    not_submitted_df.loc[not_submitted_df['status'] != np.nan, 'status'] = np.nan
    
    not_submitted_df['game_date'] = pd.to_datetime(not_submitted_df['game_date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')

    not_submitted_df['game_start_time'] = not_submitted_df['game_start_time'].str.replace(' (ET)', '')

    not_submitted_df['injury_report_datetime'] = not_submitted_df['injury_report_datetime'].str.replace("Injury Report: ", "")

    not_submitted_df['injury_report_datetime'] = pd.to_datetime(not_submitted_df['injury_report_datetime'], format = '%m/%d/%y %I:%M %p').dt.strftime('%Y-%m-%d %H:%M')

    not_submitted_df = not_submitted_df[['injury_report_datetime', 'game_date', 'Matchup', 'Team', 'player_name', 'status', 'reason']]

    not_submitted_df[['visitor_team_id', 'home_team_id']] = not_submitted_df['Matchup'].str.split('@', expand = True)

    not_submitted_df['player_first_name'] = np.nan

    not_submitted_df['player_last_name'] = np.nan

    not_submitted_df = not_submitted_df[['injury_report_datetime', 'game_date', 'visitor_team_id', 'home_team_id', 'Team', 'player_name', 'player_first_name', 'player_last_name', 'status', 'reason']]

    full_injury_df = pd.concat([concat_df, not_submitted_df], ignore_index = True)

    full_injury_df.to_csv('full_injury_csv')


