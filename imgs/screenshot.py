import os
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

GRAPHS_URL = "https://chriswmartin.github.io/ohio-covid19/"
SCHOOLS_URL = "https://chriswmartin.github.io/ohio-covid19/schools/index.html"

GRAPHS_IMG = "graphs.png"
SCOOLS_IMG = "schools.png"
COMBINED_IMG = "combined.png"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1000,1025")
chrome_options.add_argument("--hide-scrollbars")
graphs_driver = webdriver.Chrome(options=chrome_options)

graphs_driver.get(GRAPHS_URL)
graphs_driver.execute_script("var elements = document.querySelectorAll('h3, h4, a'); for (var i = 0; i < elements.length; i++) { elements[i].style.display = 'none' }")
graphs_screenshot = graphs_driver.save_screenshot(GRAPHS_IMG)
graphs_driver.quit()

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1000,1025")
chrome_options.add_argument("--hide-scrollbars")
schools_driver = webdriver.Chrome(options=chrome_options)

schools_driver.get(SCHOOLS_URL)
schools_driver.execute_script("var elements = document.getElementsByTagName('a'); for (var i = 0; i < elements.length; i++) { elements[i].style.display = 'none' }")
schools_screenshot = schools_driver.save_screenshot(SCOOLS_IMG)
schools_driver.quit()

def combine_imgs(img1, img2):
    combined = Image.new('RGB', (img1.width + img2.width, img1.height))
    combined.paste(img1, (0, 0))
    combined.paste(img2, (img1.width, 0))
    return combined

g_img = Image.open(GRAPHS_IMG)
s_img = Image.open(SCOOLS_IMG)
combine_imgs(g_img, s_img).save(COMBINED_IMG)

if os.path.exists(GRAPHS_IMG):
  os.remove(GRAPHS_IMG)
if os.path.exists(SCOOLS_IMG):
  os.remove(SCOOLS_IMG)
