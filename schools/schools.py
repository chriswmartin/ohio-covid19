import requests
import numbers
import csv
import re
import locale
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.progress import track

locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

URL = "https://coronavirus.ohio.gov/static/dashboards/school_reporting.csv"
FILE = "data/school_reporting.csv"

def download_data(url):
    data = {}
    with requests.Session() as s:
        download = s.get(url)
        decoded_content = download.content.decode('utf-8')
        reader = csv.reader(decoded_content.splitlines(), delimiter=',')
        data = {rows[1]:rows[4] for rows in reader}
    return data

def get_num_students(school):
    school_encoded = school.replace(" ", "+")
    url = 'https://www.google.com/search?client=firefox-b-1-d&q=' + school_encoded + '+school+ohio+number+of+students'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    results = soup.find_all('div', class_=["Z0LcW", "XcVN5d"])
    for result in results:
        number_of_students = re.sub('[^0-9,]', "", result.text)
        return locale.atoi(number_of_students)

def file_prepend(input_file, string):
    with open(input_file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(string.rstrip('\r\n') + '\n' + content)

data = download_data(URL)

for key, value in list(data.items()):
    if value.isnumeric():
        data[key] = int(value)
    else:
        del data[key]

table = Table(title="Top Schools")
table.add_column("School name",  style="blue", no_wrap=True)
table.add_column("Total cases", style="red")
table.add_column("Number of students", style="green")
table.add_column("Percentage", style="cyan")

top_schools = sorted(data, key=data.get, reverse=True)[:20]
# for school in top_schools:
for school in track(top_schools):
    school_name = school
    number_of_students = get_num_students(school)
    if number_of_students is None:
        number_of_students = "N/A"
    total_cases = data[school]
    if type(number_of_students) is int:
        percentage = "{:.2%}".format(total_cases / number_of_students)
    else:
        percentage = "N/A"
    table.add_row(str(school_name), str(total_cases), str(number_of_students), str(percentage))

console = Console(record=True)
console.print(table)
console.save_html('index.html')

style_html = "<style>body { text-align: center; font-family: monospace; margin: 2%; }</style>"
graphs_link_html = "<a href='/ohio-covid19/'>graphs</a>"

file_prepend('index.html', style_html)

html_file = open('index.html', "a")
html_file.writelines(graphs_link_html)
html_file.close()
