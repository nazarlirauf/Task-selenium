import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

print("Test script started...")
time.sleep(3)


def get_driver():
    selenium_grid_url = "http://selenium-hub:4444/wd/hub"  
    

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    

    driver = webdriver.Remote(command_executor=selenium_grid_url, options=chrome_options)
    driver.maximize_window()
    print("Connected to Selenium Grid successfully.")
    return driver

def test_homepage_open():
    driver = get_driver()
    try:
        driver.get("https://useinsider.com")
        assert "Insider" in driver.title
        print("test_homepage_open: PASSED")
    except Exception as e:
        print("An error occurred in test_homepage_open:", e)
    finally:
        driver.quit()

def test_careers_page():
    driver = get_driver()
    try:
        driver.get("https://useinsider.com")
        driver.find_element(By.LINK_TEXT, "Company").click()
        driver.find_element(By.LINK_TEXT, "Careers").click()
        
        assert "Careers" in driver.page_source
        assert "Locations" in driver.page_source
        assert "See all teams" in driver.page_source
        assert "Life at Insider" in driver.page_source
        print("test_careers_page: PASSED")
    except Exception as e:
        print("An error occurred in test_careers_page:", e)
    finally:
        driver.quit()

def test_qa_jobs_filter_and_view_role_redirection():
    driver = get_driver()
    driver.get("https://useinsider.com/careers/quality-assurance/")
    
    try:
        cookie_banner = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "wt-cli-cookie-banner")))
        accept_cookies_button = driver.find_element(By.ID, "wt-cli-reject-btn")
        accept_cookies_button.click()
        print("Cookie banner closed.")
    except Exception as e:
        print("Cookie banner not found or could not be closed:", e)
        
    driver.find_element(By.LINK_TEXT, "See all QA jobs").click()
    print("See all QA jobs was clicked")
    time.sleep(3)
    
    filter_button = driver.find_element(By.ID, 'select2-filter-by-location-container')
    filter_button.click()
    time.sleep(2)
    filter_button.click()
    time.sleep(10)
    filter_button.click()
    time.sleep(1)

    istanbul = driver.find_elements(By.CLASS_NAME, 'select2-results__option')
    istanbul[1].click()
    print("Istanbul was selected")

    filter_button = driver.find_element(By.ID, 'select2-filter-by-department-container')
    filter_button.click()
    time.sleep(2)
    filter_button.click()
    time.sleep(10)
    filter_button.click()
    time.sleep(1)

    qa = driver.find_elements(By.CLASS_NAME, 'select2-results__option')
    qa[-1].click()
    print("QA was selected")
    
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script(f"window.scrollTo(0, {total_height / 3});")
    time.sleep(3)

    jobs = driver.find_elements(By.ID, "jobs-list") 
    
    for job in jobs:
        assert "Quality Assurance" in job.text
        assert "Istanbul, Turkey" in job.text
        
    print("test_qa_jobs_filter: PASSED")
    
    button_xpath = "//a[contains(@href, 'jobs.lever.co/useinsider/78ddbec0-16bf-4eab-b5a6-04facb993ddc')]"
    button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, button_xpath)))
    
    driver.execute_script("arguments[0].scrollIntoView(true);", button)
    button.click()
    print("View Role was clicked")
    time.sleep(3)  
    

    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])
        print(driver.current_url)
        assert "lever" in driver.current_url
        print("test_view_role_redirection: PASSED")
    else:
        print("new window not openned.")
    
    driver.quit()

test_homepage_open()
test_careers_page()
test_qa_jobs_filter_and_view_role_redirection()
