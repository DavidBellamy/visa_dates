import matplotlib.pyplot as plt
import pandas as pd


countries = ['India', 'China', 'Mexico', 'Philippines', 'RoW']

for country in countries:
    df = pd.read_csv(f'data/{country.lower()}_visa_backlog_timecourse.csv')
    df['visa_bulletin_date'] = pd.to_datetime(df['visa_bulletin_date'])
    df['visa_wait_time'] = df['visa_wait_time'].astype(float)

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))
    fig.suptitle(f'Employment-based visa wait times for {country}')

    for i in range(1, 5):
        ax = axs[(i-1)//2, (i-1)%2]
        data = df[df['EB_level'] == i]
        ax.plot(data['visa_bulletin_date'], data['visa_wait_time'])
        ax.set_title(f'EB-{i}')
        ax.set_xlabel('Time')
        ax.set_ylabel('Visa wait time (years)')

    plt.tight_layout()
    plt.savefig(f'figures/{country}_visa_wait_times.png')
