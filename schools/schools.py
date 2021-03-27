import io
import re
import locale
import requests
import pandas as pd
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.progress import track

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

URL = "https://coronavirus.ohio.gov/static/dashboards/school_reporting.csv"
FILE = "data/school_reporting.csv"

def download_data(url):
    urlData = requests.get(url).content
    df = pd.read_csv(io.StringIO(urlData.decode('utf-8')), usecols=['school_or_school_district', 'student_cases_new', 'student_cases_cumulative', 'staff_cases_new', 'staff_cases_cumulative'], header=0)
    data = df.to_dict(orient='records')
    return data

def get_num_students(school):
    school_encoded = school.replace(" ", "+")
    url = 'https://www.google.com/search?q=' + school_encoded + '+school+ohio+number+of+students'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    # scrape google instant answers for school enrollment numbers
    # they are usually located in <div class="Z0LcW XcVN5d">
    # but I wouldn't be suprised if that changes in the future
    results = soup.find_all('div', class_=["Z0LcW", "XcVN5d"])
    for result in results:
        # extract just the enrollment number string
        number_of_students = re.sub('[^0-9,]', "", result.text)
        # cast the enrollment number string (typically xx,xxx) into an int
        return locale.atoi(number_of_students)

def file_prepend(input_file, string):
    with open(input_file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(string.rstrip('\r\n') + '\n' + content)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

raw_data = download_data(URL)

data = []
for entry in raw_data:
    total_cases = 0

    new_cases = ['student_cases_new', 'staff_cases_new']
    cumulative_cases = ['student_cases_cumulative', 'staff_cases_cumulative']
    
    for case in cumulative_cases:
        if entry[case].isnumeric() or is_number(entry[case]) == True:
            entry[case] = int(entry[case])
            total_cases += entry[case]
        else:
            entry[case] = 0
    entry['total_cases'] = total_cases
    
    for case in new_cases:
        if entry[case].isnumeric() == False:
            entry[case] = 0
    data.append(entry)

table = Table(title="Top Schools")
table.add_column("School name",  style="blue", no_wrap=True)
table.add_column("Total cases", style="red", no_wrap=False)
table.add_column("New student cases", style="magenta", no_wrap=False)
table.add_column("New staff cases", style="magenta", no_wrap=False)
table.add_column("Number of students (est.)", style="green", no_wrap=False)
table.add_column("Percentage (est.)", style="cyan", no_wrap=False)

NUMBER_OF_SCHOOLS = 25
top_schools = sorted(data, key=lambda i: i['total_cases'], reverse=True)[:NUMBER_OF_SCHOOLS]
for school in track(top_schools):
    school_name = school['school_or_school_district']
    total_cases = school['total_cases']
    new_student_cases = school['student_cases_new']
    new_staff_cases = school['staff_cases_new']
    number_of_students = get_num_students(school_name)
    if number_of_students is None:
        number_of_students = "N/A"
    if type(number_of_students) is int:
        percentage = "{:.2%}".format(total_cases / number_of_students)
    else:
        percentage = "N/A"
    table.add_row(str(school_name), str(total_cases), str(new_student_cases), str(new_staff_cases), str(number_of_students), str(percentage))

console = Console(record=True)
console.print(table)
console.save_html('index.html')

style_html = "<style>body { text-align: center; font-family: monospace; margin: 2%; }</style>"
graphs_link_html = "<a href='/ohio-covid19/'>graphs</a>"

file_prepend('index.html', style_html)

html_file = open('index.html', "a")
html_file.writelines(graphs_link_html)
html_file.close()
