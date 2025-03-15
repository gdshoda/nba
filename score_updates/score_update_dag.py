def get_score_data():
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    url = "https://www.basketball-reference.com/leagues/NBA_2025_games-{{ execution_date.strftime('%B').lower() }}.html"


    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'schedule'})
    rows = table.find_all('tr')[1:]

    game_data = []

    for row in rows:
        cols = row.find_all('td')

        if cols:
            game_date = row.find('th').text.strip()
            away_team = cols[1].text.strip()
            home_team = cols[3].text.strip()
            away_score = cols[2].text.strip()
            home_score = cols[4].text.strip()
            if home_score:
                overtime = cols[6].text.strip() if cols[6].text.strip() else "n"
            else:
                overtime = ""

            game_data.append([game_date, away_team, home_team, away_score, home_score, overtime])
    df = pd.DataFrame(game_data, columns=['Date', 'Away Team', 'Home Team', 'Away Score', 'Home Score', 'Overtime'])
    df['Date'] = pd.to_datetime(df['Date'], format = "%a, %b %d, %Y").dt.date
