import sys
import time 
from datetime import datetime
from calendar import Calendar, monthrange
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def promptInput(message, ifEmptyMessage):
    _input = input(message)
    if not _input:
        raise Exception(ifEmptyMessage)
    return _input


# sample input
# username = "user001"
# password = "p@ssw0rd"
# strdate = "202108"

username = promptInput("Login Username: ", "username cannot be empty")
password = promptInput("Login Password: ", "password cannot be empty")
strdate = promptInput("Date (format yyyymm e.g. 202101): ", "Date cannot be empty")


try:
    Month = datetime.strptime(strdate, "%Y%m").date()
except ValueError as e:
    raise Exception("Error :: Wrong date format, expected format in 202101") 

print("executing script with username", username, ", password", password, ", date", Month.strftime("%B %Y"))

confirm = input("Confirm? (Y/N): ")
# confirm = "N"
if confirm.upper() == "Y":
    try:
        URL = "<<TimesheetPortalUrl>>"
        DRIVER_PATH = "./driver/chromedriver"
        TIMEOUT = 10
        
        print("Initialize Driver ...")
        option = webdriver.ChromeOptions()
        option.add_argument("-incognito")
        option.add_experimental_option("detach", True)
        # option.add_experimental_option("excludeSwitches", ["enable-automation"])
        # option.add_argument("--headless")
        # option.add_argument("disable-gpu")

        print("Opening Browser ...")
        browser = webdriver.Chrome(executable_path=DRIVER_PATH, options=option)
        browser.get(URL)

        # login page
        print("Navigate to Login Page")
        print("logging in with username and password ...")
        usernameInput = WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.NAME, "TMP_USR_ID"))).send_keys(username)
        passwordInput = browser.find_element_by_name("TMP_PASSWD").send_keys(password)
        browser.find_element_by_name("submit").click()

        # home page
        print("Navigate to Home Page")
        print("selecting Task menu ...")
        taskMenu = WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Task')]"))).click()

        # task page
        print("Navigate to Task Page")
        print("selecting target month ...")
        WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//select[@name='T_MM']/option[text()='%s']" % Month.strftime("%b").upper() ))).click() #JAN
        #TODO should select year as well
        browser.find_element_by_xpath("//input[@value='Go']").click()

        # start loop date and fill form
        calendar = Calendar()
        month = int(Month.strftime("%m"))
        year = int(Month.strftime("%Y"))
        for d in calendar.itermonthdates(year, month):
            if d.month == month and d.weekday() < 5:
                formattedDate = d.strftime("%d/%m/%Y") #01/01/2021
                print("filling for date %s ..." % formattedDate)
                WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//input[@value='%s']" % formattedDate)))
                browser.find_element_by_xpath("//a[contains(@href, '%s')]" % d.strftime("%Y%m%d")).click() #20210101
                # within form page
                WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//select[@name='<<ProjectID>>']/option[text()='<<ProjectNameAndDescription>>']"))).click()
                browser.find_element_by_xpath("//select[@name='<<ProjectStatus>>']/option[text()='In Project']").click()
                browser.find_element_by_xpath("//select[@name='<<ProjectStartHour>>']/option[text()='09']").click()
                browser.find_element_by_xpath("//select[@name='<<ProjectStartMinute>>']/option[text()='00']").click()
                browser.find_element_by_xpath("//select[@name='<<ProjectEndHour>>']/option[text()='18']").click()
                browser.find_element_by_xpath("//select[@name='<<ProjectEndMinute>>']/option[text()='00']").click()
                # save and wait and back
                browser.find_element_by_xpath("//input[@value='Save']").click()
                time.sleep(3)
                browser.find_element_by_xpath("//*[contains(text(), 'Back')]").click()

    except TimeoutException:
        print("Loading took too much time!")
    except Exception as e:
        print("Unexpected Error: %s" % e)
else:
    print('Terminate Process')