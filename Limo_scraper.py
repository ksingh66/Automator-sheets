from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api import update_sheet
from api import find_row
from api import get_cell_value



def login_to_blacklane(user, passw):  # This function assumes you're on the login page. Executing this logs you in
    email_tab = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    # Wait until the password input field is visible and enabled
    password_tab = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    email_tab.send_keys(user)
    password_tab.send_keys(passw)
    password_tab.send_keys(Keys.ENTER)


def save_value(value, filename):  # This is to save the row_count for future restarts
    with open(filename, "w") as file:
        file.write(str(value))


def load_value(filename):  # This is to pull the row_count value
    try:
        with open(filename, "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 2  # Default starting row_count if file doesn't exist or is empty


def append_value(filename, value):
    with open(filename, 'a') as f:
        # Write a new line to the file
        f.write(f"{value}\n")


def load_booking_numbers(filename):
    try:
        with open(filename, "r") as file:
            return [int(line.strip()) for line in file]
    except FileNotFoundError:
        return []  # Default to an empty list if the file doesn't exist



username = "email@email.something" #You may use enviornment variables
password = "1234567890"
print("Example for April, type in : Apr")
month= input("Enter the month you want the record for (Only type in the first three letters of the month with the first letter capitalized):")
# Path to the ChromeDriver executable
chrome_driver_path = 'yourcomputer/desktop/automated-project/chromedriver' #Enter path to your chromedriver

# Setup Chrome options
chrome_options = Options()
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("WEBSITE LINK HERE")  # Go to page where all the rides are shown- We will first encounter a login page


login_to_blacklane(username, password)  # logs into website page


time.sleep(5)  # wait to let the page fully load you may also use webdriver .wait

while True:
    count = 0
    
    all_dates_nontext = driver.find_elements(By.CLASS_NAME, "Date-module__isHighlighted--1ZGgp")  # all the dates on the page
    all_dates = [date.text for date in all_dates_nontext] #This essentially parses the data into a readable format
    
    details_links = driver.find_elements(By.CLASS_NAME, 'DetailsLink-module__root--2QOZz') #The list of all the links to see the detail of each ride
    

    for date in all_dates: #We only want to click on rides that have the month we want, otherwise we want to ignore them
        if month in date:
            print(date)
            print(f"Found a date with {month}")
            # Re-locate the elements to avoid StaleElementReferenceException
            WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'DetailsLink-module__root--2QOZz')))
            details_links = driver.find_elements(By.CLASS_NAME, 'DetailsLink-module__root--2QOZz')
            
            details_link_to_click = details_links[count]
            count += 1
            driver.execute_script("arguments[0].scrollIntoView(true);", details_link_to_click)
            details_link_to_click.click()
            WebDriverWait(driver,30).until(EC.visibility_of_all_elements_located((By.CLASS_NAME,'PropertyWithTitle-module__root--fuK6S')))

            booking_number = None
            pax = None
            chauffeur = None
            pickup = None
            dropoff = None
            price = None
            date = None
            search = driver.find_elements(By.CLASS_NAME, 'PropertyWithTitle-module__root--fuK6S')
            
            list_of_details = [element.text for element in search]
            

            #Here we parse the data and seperate each detail for the ride that we want such as bookings number and price 
            for detail in list_of_details:
                if detail.startswith('Booking number'):
                    booking_number = detail.split('\n')[1]
                elif detail.startswith('Guest'):
                    pax = detail.split('\n')[1]
                elif detail.startswith('Assigned chauffeur'):
                    chauffeur = detail.split('\n')[1]
                elif detail.startswith('Pickup location'):
                    pickup = detail.split('\n')[1]
                elif detail.startswith('Dropoff location'):
                    dropoff = detail.split('\n')[1]
                elif detail.startswith('Price'):
                    price = detail.split('\n')[1]
                    price = price.split("$")[1]
                elif detail.startswith('Date'):
                    date = detail.split('\n')[1]
            


            current_month = date.split(" ")[1]

            row_count = load_value("row_count.txt") # row count is used to keep track of which row on the google sheet to write on

            #update the row with ride information
            update_sheet("A", row_count, booking_number, current_month)
            update_sheet("B", row_count, pax, current_month)
            update_sheet("C", row_count, chauffeur, current_month)
            update_sheet("D", row_count, pickup, current_month)
            update_sheet("E", row_count, dropoff, current_month)
            update_sheet("F", row_count, price, current_month)
            update_sheet("G", row_count, date, current_month)

            row_count +=1
            save_value(row_count,"row_count.txt")

            # Navigate back to the main page with finished rides
            driver.back()
            
        else:
            count = count+1
    WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.ID, 'page-next'))) #we find and click on the next page to keep loking for more rides

    next_button = driver.find_element(By.ID, "page-next")
    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
    next_button.click()
