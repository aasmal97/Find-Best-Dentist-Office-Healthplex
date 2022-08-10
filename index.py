
import pandas as pd
from utils.setup_env import setup_enviroment, search_offices, navigate_and_search
from utils.driver_actions import loop_through_data
#setup to avoid bot detection and grab driver (the automated tool)
def main(params):
    driver = setup_enviroment()
    navigate_params = {
        "driver": driver, 
        "groupNum": params["groupNum"],
        "searchPath": "//input[@placeholder='GROUP NUMBER']", 
        "btnPath": "//input[@type='submit'][@value = 'SEARCH']"
    }
    navigate_and_search(navigate_params)
    #enter search parameters on main tab
    search_offices(driver, params['searchInputs'])
    data = loop_through_data(driver)
    df = pd.DataFrame(data, columns=['Name',"Address", "Rating", "Review"])
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