import requests
#import html5lib
import bs4
from typing import Optional, Union
from dataclasses import dataclass, fields
from box import Box
from pandas import read_html, DataFrame, to_numeric


URL = 'https://fbref.com/en/players/[player_id]/matchlogs/[start_year]-[end_year]/summary/[player_first_name]-[player_last_name]-Match-Logs'


@dataclass
class Data:
    start_year: Union[str, int] = None
    end_year: Union[str, int] = None
    player_id: str = None
    player_first_name: str = None
    player_last_name: str = None


def get_player_season_matchlogs(data: Data) -> Optional[dict]:
    ''''''
    store = Box(over_headers=[], headers=[], )

    if data.end_year is None:
        data.end_year = data.start_year + 1

    # Set the URL
    url = URL
    for field in fields(data):
        url = url.replace(f'[{field.name}]', f'{getattr(data, field.name)}')
    print(url)

    # Make the request
    response = requests.get(url)
    # Failed response
    if response.status_code != 200:
        print(response.content)
        return None

    # Get page html
    soup = bs4.BeautifulSoup(response.content, features='lxml')
    # Get table
    table = soup.find('table', id='matchlogs_all')
    
    # Get table over headers
    over_header_row = table.find_all('tr', {'class': 'over_header'})
    over_headers = over_header_row[0].find_all('th')
    for item in over_headers:
        if len(item.text) == 0:
            continue
        store.over_headers.append(item.text)
        store[item.text] = []

    # Get table headers
    headers = table.find_all('th', {'scope': 'col'})
    for header in headers:
        store.headers.append(header.text)
        # Headers associated with an over header
        data_over_header = header.get('data-over-header')
        if data_over_header in store.over_headers:
            store[data_over_header].append(header.text)

    # Load table row data into dataframe
    df = read_html(table.prettify())[0]
    # Set table column names
    df.columns = store.headers
    # Remove blank rows
    df = df[df['Date'].notnull()]
    # Add player name column
    df['Player'] = f'{data.player_last_name}, {data.player_first_name}'
    df.drop(columns=['Match Report'], inplace=True)
    return df.to_dict(orient='records')


def analysis(data: dict) -> Optional[dict]:
    ''''''

    df = DataFrame(data)
    
    # Transformations
    # Premier League competitions only
    df = df[df['Squad'] == 'Manchester Utd']

    # Filter out non-numeric values
    df = df[to_numeric(df['Min'], errors='coerce').notnull()]
    df = df[df['Min'].astype(int) > 0]

    # Split result column
    df['Result_2'] = df['Result'].apply(lambda x: x.split(' ')[0])

    # Combine columns to filter for games played together
    df['combine'] = df.apply(lambda x: f"{x['Date']}_{x['Squad']}", axis=1)
    count_map = df['combine'].value_counts().to_dict()
    df['combine_counts'] = df['combine'].apply(lambda x: count_map[x])
    df_apart = df[df['combine_counts'] == 1]
    df_together = df[df['combine_counts'] > 1]


    together = Box((df_together['Result_2'].value_counts() / len(df_together)).to_dict())
    together.games = len(df_together)
    apart = (df_apart['Result_2'].value_counts() / len(df_apart)).to_dict()
    df_apart_bruno = df_apart[df_apart['Player'] == 'Fernandes, Bruno']
    df_apart_bruno = Box((df_apart_bruno['Result_2'].value_counts() / len(df_apart_bruno)).to_dict())
    df_apart_bruno.games = len(df_apart_bruno)
    df_apart_pogba = df_apart[df_apart['Player'] == 'Pogba, Paul']
    df_apart_pogba = Box((df_apart_pogba['Result_2'].value_counts() / len(df_apart_pogba)).to_dict())
    df_apart_pogba.games = len(df_apart_pogba)

    results = Box(
        together=together,
        apart=Box(bruno=df_apart_bruno, paul=df_apart_pogba), )
    print(results)

    

    # print(df[df['combine'] == '2021-02-02_Manchester Utd'])
    # for i in df['Min']:
    #     print(i)
    df.sort_values(by=['combine'], inplace=True)
    return df.to_dict(orient='records')


def main():
    data = []
    years = [2019, 2020, 2021,]
    for year in years:
        input = Data(
            start_year=year,
            player_id='867239d3',
            player_first_name='Paul',
            player_last_name='Pogba', )
        data += get_player_season_matchlogs(data=input)
        # input = Data(
        #     start_year=year,
        #     player_id='507c7bdf',
        #     player_first_name='Bruno',
        #     player_last_name='Fernandes', )
        # data += get_player_season_matchlogs(data=input)
    data = analysis(data)
    # print(data)

if __name__ == '__main__':
    main()
