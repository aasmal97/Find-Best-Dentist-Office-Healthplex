import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_element(driver, search_path, custom_time = 5):
    try:
        elem = WebDriverWait(driver, custom_time).until(
            EC.presence_of_element_located((By.XPATH, search_path)) #This is a dummy element
        )
        return elem
    except TimeoutException: 
        return None
    
def click_element(driver, elementPath):
    element = get_element(driver, elementPath)
    element.click()
def match_dynamic_regex(regex, str):
    pattern = re.compile(regex)
    strip_str = str.strip()
    substrings = re.split(r' {2,}', strip_str)
    for new_str in substrings:
        if pattern.search(new_str):
            number = re.findall('\d*\.?\d+', new_str)[0]
            return float(number)
    else: 
        return 0

def get_data_from_single_pg(driver):
    ratings_parent = get_element(driver, "//div[@jsaction='pane.rating.moreReviews'][@role = 'button']", 2)
    if ratings_parent == None: 
        return [0, 0]
    reviews_parent = get_element(driver, "//span[@jsaction='pane.rating.moreReviews']", 2)
    try:
        ratings_el = ratings_parent.find_element(By.XPATH, ".//span[@aria-label][@role = 'img']")
        reviews_el = reviews_parent.find_element(By.XPATH, ".//button[@jsaction='pane.rating.moreReviews']")
        ratings_data = ratings_el.get_attribute('aria-label')
        reviews_data = reviews_el.get_attribute('aria-label')
        return [
            match_dynamic_regex("star",ratings_data), 
            match_dynamic_regex("review",reviews_data)
        ]
    except NoSuchElementException:
        return [0, 0]
    except AttributeError:
        reviews_el = driver.find_element(By.XPATH, "//span[contains(@aria-label, 'reviews')]")
        ratings_el = driver.find_element(By.XPATH, "//span[contains(@aria-label, 'star')]")
        ratings_data = ratings_el.get_attribute('aria-label')
        reviews_data = reviews_el.get_attribute('aria-label')
        return [
            match_dynamic_regex("star",ratings_data), 
            match_dynamic_regex("review",reviews_data)
        ]
def get_data_from_list(root): 
    rating, review = [0, 0]
    ratings_els = root.find_elements(By.XPATH, "//span[contains(@aria-label, 'star')]")
    reviews_els = root.find_elements(By.XPATH, "//span[contains(@aria-label, 'Review')]")
    #we're dealing with a single page layout
    if len(ratings_els) > len(reviews_els):
        return [0, 0]
    for idx, rating_el in enumerate(ratings_els):
        review_content = reviews_els[idx].get_attribute('aria-label')
        rating_content = rating_el.get_attribute('aria-label')
        new_review = match_dynamic_regex('Review', review_content)
        new_rating = match_dynamic_regex('star', rating_content)
        is_review_higher = new_review and new_review > review
        is_rating_higher = new_rating and new_rating > rating
        if is_rating_higher and is_review_higher:
            review = new_review
            rating = new_rating
    return [rating, review]

def get_rating_and_reviews(driver): 
    #grab list and list items
    list_box = get_element(driver,"//div[@role = 'listbox']", 3)
    #initial attempt using address link
    if list_box == None:
        result =  get_data_from_list(driver)
        #means no list is found
        if result[0] == 0 and result[1] == 0:
            result = get_data_from_single_pg(driver)
        return result
    else: 
        return get_data_from_list(list_box)
def use_office_name(driver, idx):
    driver.switch_to.window(driver.window_handles[0])
    office_names = driver.find_elements(By.XPATH, "//div[contains(@class, 'name')]")
    name = office_names[idx].text
    driver.switch_to.window(driver.window_handles[1])
    search_input = driver.find_element(By.XPATH, "//input[@id = 'searchboxinput']")
    search_btn = driver.find_element(By.XPATH, "//button[@aria-label = 'Search']")
    clear_search = driver.find_element(By.XPATH, "//a[@aria-label = 'Clear search']")
    clear_search.click()
    search_input.send_keys(name)
    search_btn.click()
    return get_rating_and_reviews(driver)

def get_data(driver, address_els, data = []):
    #switch to new tab
    office_names = driver.find_elements(By.XPATH, "//div[contains(@class, 'name')]")
    names = [x.text for x in office_names]
    for idx, address in enumerate(address_els):
        text_el = address.text
        #click on link to google maps page
        address.find_element(By.XPATH, "..").click()
        driver.switch_to.window(driver.window_handles[1])
        #initial attempt will use address link
        rating, review = get_rating_and_reviews(driver)
        #we use the name of office for improved search
        if int(rating) == 0 and int(review) == 0:
            rating, review = use_office_name(driver, idx)
        new_row = [names[idx], text_el, rating, review]
        print(new_row)
        data.append(new_row)
        #set window back to search page
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    return data    
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