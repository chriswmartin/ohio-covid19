import datetime
from collections import defaultdict
import requests
import pandas
import matplotlib.pyplot as plt
import mpld3

DATA_FILE = 'data/COVIDSummaryData.csv'
def download_data():
    url = "https://coronavirus.ohio.gov/static/COVIDSummaryData.csv"
    r = requests.request('GET', url)
    with open(DATA_FILE, 'wb') as f:
        f.write(r.content)
        
def load_data(input_data):
    data = pandas.read_csv(input_data, sep=',', error_bad_lines=False, low_memory=False)
    data.drop(data.tail(1).index, inplace=True)
    data['Case Count'] = data['Case Count'].astype(int)
    data = data.groupby(['County', 'Onset Date'])['Case Count'].sum().reset_index()

    d = defaultdict(dict)
    for _, row in data.iterrows():
        row['Onset Date'] = datetime.datetime.strptime(row['Onset Date'], '%m/%d/%Y')
        d[row['County']][row['Onset Date']] = row.drop(['County', 'Onset Date']).to_dict()
    return dict(d)

def get_top_counties(num, input_data):
    counties = {}
    top_counties = {}
    for county in input_data:
        total_cases = 0
        for date in input_data[county]:
            total_cases += input_data[county][date]['Case Count']
        counties[county] = total_cases
    top_counties = {key: counties[key] for key in sorted(counties, key=counties.get, reverse=True)[:num]}
    return top_counties

def create_plot(all_data, top_data, time_offset, ax=None):
    ax = ax or plt.gca()
    for county in top_data.keys():
        tmp_date = []
        tmp_count = []
        for date in sorted(all_data[county]):
            today = datetime.datetime.now()
            day_offset = datetime.timedelta(days = time_offset)
            start_date = today - day_offset
            if date >= start_date:
                tmp_county = county
                tmp_date.append(date)
                tmp_count.append(all_data[county][date]['Case Count']) 
            ax.plot(tmp_date, tmp_count, label=county)
    return ax

download_data()
all_data = load_data(DATA_FILE)
top_data = get_top_counties(20, all_data)

time_ranges = [200, 30, 7]
fig, axs = plt.subplots(nrows=len(time_ranges), ncols=1, figsize=(10, 10))
for index, time_range in enumerate(time_ranges):
    create_plot(all_data, top_data, time_range, axs[index])

plt.set_cmap('gist_rainbow')
font = {'family' : 'Monospace',
        'weight' : 'regular',
        'size'   : 8}
plt.rc('font', **font)
plt.margins(0, 0)
plt.tight_layout()

mpld3.save_html(fig, 'index.html')
