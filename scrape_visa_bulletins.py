from typing import List, Union
import requests
import re
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm


BASE_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"

def extract_datetime_from_link(link: str) -> Union[None, datetime]:
    # Regular expression to match "visa-bulletin-for-month-year.html"
    pattern = r'visa-bulletin-for-(\w+)-(\d{4})\.html$'
    
    match = re.search(pattern, link)

    if not match:
        return None

    # Extract month and year from the matched groups
    month_str, year = match.groups()

    # Map month string to its corresponding number
    month_map = {
        'january': 1,
        'february': 2,
        'march': 3,
        'april': 4,
        'may': 5,
        'june': 6,
        'july': 7,
        'august': 8,
        'september': 9,
        'october': 10,
        'november': 11,
        'december': 12
    }

    month = month_map.get(month_str.lower())

    if not month:
        return None

    # Create a datetime object
    dt = datetime(year=int(year), month=month, day=1)

    return dt

def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def extract_month_links() -> List[str]:
    soup = get_soup(BASE_URL)
    month_links = []

    # Step 1: Find each main accordion container
    accordion_sections = soup.find_all('div', class_='accordion parbase section')

    for section in accordion_sections:
        # Step 2: Locate the div containing the links
        link_container = section.find('div', class_='tsg-rwd-accordion-copy')

        if link_container:
            # Step 3: Extract all the <a> tags
            links = link_container.find_all('a', href=True)
            
            for link in links:
                month_links.append(link['href'])

    return month_links


def extract_tables(link: str) -> List[pd.DataFrame]:
    year_month = extract_datetime_from_link(link)
    soup = get_soup('https://travel.state.gov/' + link)

    # Find all table elements
    tables = soup.find_all('table')
    
    dfs = []  # List to hold DataFrames

    for table in tables:
        rows = table.find_all('tr')
        # Search for "employment-based" in the table's rows
        if any("employment-based" in row.get_text(strip=True).lower() for row in rows):
            table_data = []
            for row in rows:
                th_cols = row.find_all('th')
                td_cols = row.find_all('td')
                
                # Combine the th and td columns, th first
                all_cols = th_cols + td_cols
                
                # Extract text from each column
                cols = [ele.text.strip() for ele in all_cols]
                table_data.append(cols)
            
            # If the first row only has one column, it is a spanning header, remove it
            if len(table_data[0]) == 1: 
                columns = table_data[1]
                table_body = table_data[2:]
            else:
                columns = table_data[0]
                table_body = table_data[1:]

            # Convert the table_data into a DataFrame, treating the first row as headers
            df = pd.DataFrame(table_body, columns=columns)
            df['visa_bulletin_date'] = year_month  # Add a column for the year_month
            df.columns = df.columns.str.replace('\n', '').str.replace('- ', '-')
            df.columns = df.columns.str.lower()
            dfs.append(df)  # Append the DataFrame to the list
            break  # Only extract the first table
    
    return dfs


def string_to_datetime(date_str: str, bulletin_date: datetime) -> Union[None, datetime]:
    # Handle special cases
    if date_str == 'C':
        return bulletin_date
    elif date_str == 'U':
        return None
    elif pd.isna(date_str):
        return None

    try:
        return datetime.strptime(date_str, '%d%b%y')
    except ValueError:
        return None
    

def extract_country_data(country: str, all_data: List[pd.DataFrame]) -> pd.DataFrame:
        country_data = []
        for df in all_data:
            # Replace non-breaking spaces with regular spaces in column names
            df.columns = [column.replace(u'\xa0', u' ') for column in df.columns]

            # for rest of the world, put country as the specific string
            if country == 'row':
                country = 'all chargeability  areas except those listed'

            if any([country in col for col in df.columns]):
                col_idx = [i for i, col in enumerate(df.columns) if country in col][0]
                country_col = df.columns[col_idx]
                try:
                    df = df[['employment-based', country_col, 'visa_bulletin_date']]
                    df.columns = df.columns.str.replace(country_col, 'final_action_dates')
                    df.columns = df.columns.str.replace('employment-based', 'EB_level')
                    country_data.append(df)
                except:
                    pass
        
        country_df = pd.concat(country_data, axis=0, ignore_index=True)

        # calculate backlog period length (difference in months between 'india' and 'bulletin_year_month')
        country_df['final_action_dates'] = country_df.apply(lambda row: string_to_datetime(row['final_action_dates'], row['visa_bulletin_date']), axis=1)
        country_df['visa_wait_time'] = country_df.apply(lambda row: (row['visa_bulletin_date'] - row['final_action_dates']).days / 365.25, axis=1)
        
        # In column "EB_level", sub values "1st", "2nd", "3rd", "4th", for the integers 1, 2, 3, 4
        country_df['EB_level'] = country_df['EB_level'].str.replace('st', '').str.replace('nd', '').str.replace('rd', '').str.replace('th', '')

        # Filter all other EB levels/description besides 1-4
        country_df = country_df[country_df['EB_level'].isin(['1', '2', '3', '4'])]

        return country_df

def main():
    month_links = extract_month_links()
    
    all_data = []
    for i, link in tqdm(enumerate(month_links), total=len(month_links), 
                        desc="Extracting all employment-based visa bulletin tables"):
        table_data = extract_tables(link)
        all_data.extend(table_data)

    countries = ['india', 'china', 'mexico', 'philippines', 'row']
    for country in tqdm(countries, desc=f"Extracting data for each country and computing backlogs"):
        country_df = extract_country_data(country, all_data)
        country_df = country_df.sort_values(by='visa_bulletin_date', ascending=False)
        country_df.to_csv(f'data/{country}_visa_backlog_timecourse.csv', index=False)


if __name__ == "__main__":
    main()
