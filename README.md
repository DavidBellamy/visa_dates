# Visa Bulletin Scraper

This codebase is designed to scrape employment-based visa bulletin data from the [U.S. Department of State's website](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html) and process it into a structured CSV file for each country: India, China, Mexico and Philippines. The main script is `scrape_visa_bulletins.py` andthe scraped data by country is in `data/`.

## Visualizing visa wait-times
I've included a basic time series visualization of the EB-1 through EB-4 visa wait times for each country mentioned above in `figure/`. You can also take the `.csv` files from `data/` and upload them to ChatGPT-4 (with the advanced data analysis extension enabled) and ask it to make any figures you want. Good luck!

## Dependencies

The scraper requires the following Python libraries, which can be installed using pip:

- pandas
- tqdm
- matplotlib
- beautifulsoup4

In your Python environment, install all dependencies using the following command:

```
pip install -r requirements.txt
```

## How it Works

The script works by first extracting links to monthly visa bulletins from the [main page](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html). Each link is then visited to extract employment-based visa tables. For each country, this tabular data is then cleaned and processed, including converting date strings to datetime objects, calculating the backlog period, and renaming columns for clarity.

## Output

The output is a CSV file named india_visa_bulletin_data.csv with the following columns:

- EB_level: The employment-based visa level (1, 2, 3, 4).
- final_action_dates: The final action date for the visa.
- visa_bulletin_date: The date of the monthly visa bulletin.
- visa_wait_time: The calculated wait time for the visa *in years*.

## Running the Script

To run the web scraping script, simply execute the `scrape_visa_bulletins.py` file. The script is designed to be run as a standalone program in about 2 minutes, depending on the speed of your internet connection:

```shell
python scrape_visa_bulletins.py
```

To run the visualization script, simply execute the `visualize_visa_wait_times.py` file. 

```shell
python visualize_visa_wait_times.py
```

## Note

As with any web scraping, this script is designed specifically for the U.S. Department of State website's HTML structure as of the time of writing (Sep. 24, 2023). If the website structure changes in the future, the script may need to be updated.
