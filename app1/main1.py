from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

# Init app
app = Flask(__name__)
@app.route('/Scrape1', methods=['POST'])

def find_data():
    # Init headless ChromeDriver
    chrome_path = r'C:\Users\adamr\chromedriver_win32\chromedriver.exe'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path = chrome_path, chrome_options=chrome_options)
    driver.set_window_size(1920, 1080)
    url = 'https://foodlicensing.fssai.gov.in/index.aspx'
    
    # Recieve JSON data as dictionary
    inputs = request.get_json()
    # Parse Inputs
    instate = str(inputs.get('state'))
    inregnum = inputs.get('registration_num')
    # Go to URL
    try:
        driver.get(url)
        driver.find_element_by_xpath('//*[@id="demo-tabs-vertical"]/ul[2]/li[2]').click()
    except NoSuchElementException:
        driver.find_element_by_link_text('Click here to Refresh').click()

    # Click on the 'FBO Search' tab
    try:    
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'demo-tabs-vertical')))
        driver.find_element_by_xpath('//*[@id="demo-tabs-vertical"]/ul[2]/li[2]').click()
    except StaleElementReferenceException:
        print('Its taking too long!')
    
    ## Fill in Form with provided inputs
    
    # Find the matching State
    select0 = Select(driver.find_element_by_xpath('//*[@id="ctl00_content_ddlState"]'))
    print([o.text for o in select0.options])
    select0.select_by_visible_text(instate)
    # Enter License/Registration number
    if inregnum != '':
        try:
            select3 = driver.find_element_by_xpath('//*[@id="ctl00_content_txtLicense"]')
            select3.click
            select3.send_keys(inregnum)
            select3.submit()
        except StaleElementReferenceException:
            select3 = driver.find_element_by_xpath('//*[@id="ctl00_content_txtLicense"]')
            select3.click
            select3.send_keys(inregnum)
            select3.submit()
    # Click search
    driver.find_element_by_xpath('//*[@id="ctl00_content_btnsearch"]').click()
    # Wait for new tab to load
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'ctl00_content_update')))
    except TimeoutException:
        print('Results took too long to load!')

    # Switch active tad to search results
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    
    # Click on 'view products' hyperlink
    driver.find_element_by_xpath('//*[@id="ctl00_content_gvDetails_ctl02_lnkProduct"]').click()
    
    # Wait for new tab to load
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ctl00_content_RG_Business_GDV_FoodItems')))
    except TimeoutException:
        print('Results took too long to load!')
    
    # Switch active tad to search results
    window2 = driver.window_handles[-1]
    driver.switch_to.window(window2)    
    
    # Scrape Data
    info = []
    row_number = 1
    try:
        rows = driver.find_element_by_xpath('//*[@id="ctl00_content_RG_Business_GDV_FoodItems"]/tbody').find_elements_by_tag_name('tr')
        for row in rows:
            cells = row.find_element_by_xpath('//*[@id="ctl00_content_RG_Business_GDV_FoodItems"]/tbody/tr['+str(row_number)+']').text
            name = cells.split(" - ")[1]
            info.append(name)
            row_number += 1
    except NoSuchElementException:
        rows = driver.find_element_by_xpath('//*[@id="ctl00_content_SL_SALES_gvrestaurent"]/tbody').find_elements_by_tag_name('tr')
        for row in rows:
            cells = row.find_element_by_xpath('//*[@id="ctl00_content_SL_SALES_gvrestaurent"]/tbody/tr['+str(row_number)+']').text
            name = cells.split(" - ")
            name = name[1:]
            info.append(name)        
            row_number += 1
    info = info[1:]
    
    return jsonify(info)

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)