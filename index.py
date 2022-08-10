
import re
import os
from utils.driver_actions import get_element, click_element, get_data
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pandas as pd
# from selenium.common.exceptions import ElementNotInteractableException, ElementNotSelectableException, StaleElementReferenceException
#setup to avoid bot detection and grab driver (the automated tool)
def setup_enviroment():
    os.environ['PATH'] +=  os.pathsep + r"C:/chromeDriver"
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
    return driver

def navigate_and_search(params):
    params["driver"].get("https://www.healthplex.com/our_dentists")
    #user is given 40 sec to manually type in username and click next
    elem = get_element(params['driver'], params['searchPath'])
    elem.send_keys(params['groupNum'])
    click_element(params['driver'], params['btnPath'])

def search_offices(driver, search_params):
    specialty = Select(get_element(driver, "//select[@name='specialty']"))
    city = get_element(driver, "//input[@name='city']")
    state = Select(get_element(driver, "//select[@name='state']"))
    zip = get_element(driver, "//input[@name='zipcode']")
    miles = Select(get_element(driver, "//select[@name='distance']"))
    specialty.select_by_visible_text(search_params['specialty'])
    if 'zip' in search_params and 'miles' in search_params:
        zip.send_keys(search_params['zip'])
        miles.select_by_value(search_params['miles'])
    else: 
        city.send_keys(search_params['city'])
        state.select_by_value(search_params['state'])
     
    click_element(driver, "//button[@id = 'option-search-btn']")
def loop_through_data(driver):
    data = []
    #grab all elements that contain addresses
    pagination_list = get_element(driver, "//ul[@class = 'pagination']")
    next_list_item = pagination_list.find_element(By.XPATH, ".//li[contains(@class, 'next')]")
    next_item_classes = next_list_item.get_attribute("class")
    pattern = re.compile('disabled')
    while pattern.search(next_item_classes) == None: 
        get_element(driver, "//div[@class = 'address']", 30)
        address_els = driver.find_elements(By.XPATH, "//div[@class = 'address']")
        data += get_data(driver, address_els)
        link = next_list_item.find_element(By.XPATH, ".//a[@href = '#']")
        link.click()
        #click on element
        pagination_list = get_element(driver, "//ul[@class = 'pagination']", 10)
        next_list_item = pagination_list.find_element(By.XPATH, ".//li[contains(@class, 'next')]")
        next_item_classes = next_list_item.get_attribute("class")
    return data

def main(params):
    driver = setup_enviroment()
    navigate_params = {
        "driver": driver, 
        "groupNum": params["groupNum"],
        "searchPath": "//input[@placeholder='GROUP NUMBER']", 
        "btnPath": "//input[@type='submit'][@value = 'SEARCH']"
    }
    navigate_and_search(navigate_params)
    # [main_tab, google_maps_tab] = open_google_maps_tab(driver)
    #enter search parameters on main tab
    search_offices(driver, params['searchInputs'])
    data = loop_through_data(driver)
    print(data)
    df = pd.DataFrame(data, columns=["Address", "Rating", "Review"])
    df.to_csv("results.csv")
if __name__ == "__main__":
    main({
        "groupNum": "GL237-0801",
        "searchInputs": {
            "specialty": 'General Practice',
            # "zip": '11201',
            "city": 'Brooklyn',
            # "miles": 
            "state": 'NY'
        }
    })