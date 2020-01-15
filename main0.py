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
@app.route('/Scrape0', methods=['POST'])

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
    inbizname = str(inputs.get('business_name'))
    indist = str(inputs.get('district'))
    inregnum = inputs.get('registration_num')
    inbizkind = str(inputs.get('business_kind'))
    inproddesc = str(inputs.get('product_desc'))
    # Go to URL
    try:
        driver.get(url)
        driver.find_element_by_xpath('//*[@id="demo-tabs-vertical"]/ul[2]/li[2]').click()
    except NoSuchElementException:
        driver.find_element_by_link_text('Click here to Refresh').click()

    # Click on the 'FBO Search' tab
    try:    
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'demo-tabs-vertical')))
        driver.find_element_by_xpath('//*[@id="demo-tabs-vertical"]/ul[2]/li[2]').click()
    except StaleElementReferenceException:
        print('Its taking too long!')
    
    ## Fill in Form with provided inputs
    
    # Find the matching State
    select0 = Select(driver.find_element_by_xpath('//*[@id="ctl00_content_ddlState"]'))
    print([o.text for o in select0.options])
    select0.select_by_visible_text(instate)
    # Find the matchin District
    if indist != '':
        select1 = Select(driver.find_element_by_xpath('//*[@id="ctl00_content_ddlDistrict"]'))
        print([o.text for o in select1.options])
        select1.select_by_visible_text(indist)
    # Enter Company Name
    if inbizname != '':
        try:
            select2 = driver.find_element_by_xpath('//*[@id="ctl00_content_txtName"]')
            select2.click()
            select2.send_keys(inbizname)
            select2.submit()
        except StaleElementReferenceException:
            select2 = driver.find_element_by_xpath('//*[@id="ctl00_content_txtName"]')
            select2.click()
            select2.send_keys(inbizname)
            select2.submit()   
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
    # Select Kind of Business
    if inbizkind != '':
        select4 = Select(driver.find_element_by_xpath('//*[@id="ctl00_content_ddlKOB"]'))
        print([o.text for o in select4.options])
        select4.select_by_visible_text(inbizkind)
    # Enter Product Description
    if inproddesc != '':
        try:
            select5 = driver.find_element_by_xpath('//*[@id="ctl00_content_txtProduct"]')
            select5.click()
            select5.send_keys(inproddesc)
            select5.submit()
        except StaleElementReferenceException:
            select5 = driver.find_element_by_xpath('//*[@id="ctl00_content_txtProduct"]')
            select5.click()
            select5.send_keys(inproddesc)
            select5.submit()
    # Click search
    driver.find_element_by_xpath('//*[@id="ctl00_content_btnsearch"]').click()
    # Wait for new tab to load
    try:
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.ID, 'ctl00_content_update')))
    except TimeoutException:
        print('Results took too long to load!')

    # Switch active tad to search results
    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    # Handle Pagination
    try:
        select6 = Select(driver.find_element_by_xpath('//*[@id="ctl00_content_ddlPage"]'))
        print([o.text for o in select6.options])
        select6.select_by_visible_text('300')
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ctl00_content_update')))
        except TimeoutException:
            print('Results took too long to load!')
    except NoSuchElementException:
        print('No pagination!')
    
    # Scrape Data
    info = []
    rows = driver.find_element_by_xpath('//*[@id="ctl00_content_gvDetails"]/tbody').find_elements_by_tag_name('tr')
    row_number = 1
    for row in rows:
        try:
            row_number += 1
            name = driver.find_element_by_xpath('//*[@id="ctl00_content_gvDetails_ctl0'+str(row_number)+'_lblCompany"]').text
            address = driver.find_element_by_xpath('//*[@id="ctl00_content_gvDetails_ctl0'+str(row_number)+'_lblAdd"]').text
            registration = driver.find_element_by_xpath('//*[@id="ctl00_content_gvDetails_ctl0'+str(row_number)+'_lblLic"]').text
            info.append([name, address, registration])
        except NoSuchElementException:
            print('This is the first row!')
    
    
    return jsonify(info)

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)