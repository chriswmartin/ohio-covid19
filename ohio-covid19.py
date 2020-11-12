import datetime
from collections import defaultdict
import requests
import pandas
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins

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

def get_last_update_timestamp(data):
    all_dates = []
    for county in data:
        for date in all_data[county].keys():
            all_dates.append(date)
    return str(max(all_dates).date())

def get_num_cases_over_time_peroid(data, list_of_dates):
    num_cases = 0
    for county in data:
        for date in all_data[county].keys():
            if date.date() in list_of_dates:
                num_cases += all_data[county][date]['Case Count']
    return num_cases

def file_prepend(input_file, string):
    with open(input_file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(string.rstrip('\r\n') + '\n' + content)

download_data()
all_data = load_data(DATA_FILE)
top_data = get_top_counties(20, all_data)
last_update_timestamp = get_last_update_timestamp(all_data)

today = datetime.datetime.now().date()
seven_day_offset = datetime.timedelta(days = 7)
seven_days_ago = today - seven_day_offset
fourteen_days_ago = seven_days_ago - seven_day_offset
past_seven_days = [seven_days_ago + datetime.timedelta(days=x) for x in range((today-seven_days_ago).days + 1)]
previous_seven_days = [fourteen_days_ago + datetime.timedelta(days=x) for x in range((seven_days_ago-fourteen_days_ago).days + 1)]

current_seven_day_cases = get_num_cases_over_time_peroid(all_data, past_seven_days)
previous_seven_day_cases = get_num_cases_over_time_peroid(all_data, previous_seven_days)
seven_day_change = str(round((current_seven_day_cases - previous_seven_day_cases) / previous_seven_day_cases * 100, 2)) + "%"

time_ranges = [200, 30, 7]
fig, axs = plt.subplots(nrows=len(time_ranges), ncols=1, figsize=(10, 10))
for index, time_range in enumerate(time_ranges):
    create_plot(all_data, top_data, time_range, axs[index])

handles, labels = axs[0].get_legend_handles_labels()
axs[0].legend(handles, labels, bbox_to_anchor=(0., 1.20, 1., .120), loc='center', ncol=10, mode="expand", borderaxespad=0.0)
interactive_legend = plugins.InteractiveLegendPlugin(zip(handles, axs[0].collections), labels, alpha_unsel=0.5, alpha_over=1.5, start_visible=True)
plugins.connect(fig, interactive_legend)

plt.set_cmap('gist_rainbow')
font = {'family' : 'Monospace',
        'weight' : 'regular',
        'size'   : 10}
plt.rc('font', **font)
plt.margins(0, 0)
plt.tight_layout()

mpld3.save_html(fig, 'index.html')

seven_day_change_html = "<h3>Change: " + seven_day_change + "</h3>"
previous_seven_day_cases_html = "<h3>Previous seven day cases: " + str(previous_seven_day_cases) + "</h3>"
current_seven_day_cases_html = "<h3>Current seven day cases: " + str(current_seven_day_cases) + "</h3>"
style_html = "<style>body { text-align: center; font-family: monospace; margin-top: 1%; }</style>"
viewport_html = "<meta name='viewport' content='width=device-width, initial-scale=0.5'>"
last_update_timestamp_html = "<h4>Last updated: " + last_update_timestamp + "</h4>"
schools_link_html = "<a href='schools/index.html'>school data</a>"

file_prepend('index.html', seven_day_change_html)
file_prepend('index.html', previous_seven_day_cases_html)
file_prepend('index.html', current_seven_day_cases_html)
file_prepend('index.html', style_html)
file_prepend('index.html', viewport_html)

html_file = open('index.html', "a")
html_file.writelines(last_update_timestamp_html)
html_file.writelines(schools_link_html)
html_file.close()
