from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import config
from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
import smtplib
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import os
from Google import create_service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# print("open virtual display")
with Display():


 print("open Firefox browser")
#Change this to your own chromedriver path!
#driver = webdriver.Chrome()  # looks in /usr/local/bin

# Option 1 - with ChromeOptions
 firefox_options = webdriver.FirefoxOptions()
 firefox_options.add_argument('--headless')
 firefox_options.add_argument('--window-size=1920,1080')
 firefox_options.add_argument('--ignore-certificate-errors')

 firefox_options.add_argument(
    'user-agent="MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"')
# required when running as root user. otherwise you would get no sandbox errors.
 firefox_options.add_argument('--no-sandbox')
#driver = webdriver.Chrome( chrome_options=chrome_options,
#                          service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])
 driver = webdriver.Firefox(options=firefox_options)
 print("open Firefox browser")

 driver.set_window_size(1120, 550)

#hvis fly bliver anulleret får du penge retur, men det kan resulture i at du ikke når dit andet fly, som ikke kun refunderes. Tur-retur er derfor fordelagtigt.


 def srape_flights(from_location, to_location, from_date, to_date, flexible=False):
   #https://www.kayak.dk/flights/CPH-LCA/2022-07-11/2022-07-20-flexible-2days/2adults?sort=bestflight_a
   #
   URL = 'https://www.kayak.dk/flights/{from_location}-{to_location}/{from_date}/{to_date}/2adults?sort=bestflight_a'.format(
         from_location=from_location, to_location=to_location, from_date=from_date, to_date=to_date)

  #kayak = 'https://www.kayak.dk/flights/CPH-LCA/2022-07-14/2022-07-25/2adults?sort=bestflight_a'
   driver.get(URL)
   print(driver.page_source)
   print('start sleep')
   sleep(5)
   print('end sleep')
   print(driver.page_source)

   try:
      class_popup_close = '//div[@class = "dDYU-close dDYU-mod-variant-default dDYU-mod-size-default"]'

      print(driver.find_element_by_xpath(class_popup_close).click())
   except:
      print('error closing pop up')
      #pass

   out_time_list = []
   return_time_list = []

   out_stops = []
   return_stops = []

   out_durations = []
   return_durations = []

   out_dates = []
   return_dates = []

   prices = []
   company_names_list = []

   flight_urls = []

  #Loads 16 results more
#   try:
#       more_results = '//a[@class = "moreButton"]'
#       driver.find_element_by_xpath(more_results).click()
#       print('sleeping.....')
#       sleep(randint(25, 35))
#   except:
#       pass
   flight_rows = driver.find_elements_by_xpath('//div[@class="resultWrapper"]')
  # convert flights_rows to html so beatufiul soup can understand it
   print(flight_rows)
   for WebElement in flight_rows:

     elementHTML = WebElement.get_attribute('outerHTML')
     elementSoup = BeautifulSoup(elementHTML, 'html.parser')
     inner_grid = elementSoup.find("div", {"class": "inner-grid keel-grid"})

    # price
     temp_price = inner_grid.find(
         "div", {"class": "col-price result-column js-no-dtog"})
     price = temp_price.find(
        "span", {"class": "price-text"})
    #print(price.text)
     formatted_price = int(price.text[1:-5].replace(".", ""))

     prices.append(formatted_price)

    #company names
     company_names = inner_grid.find(
         "span", {"class": "codeshares-airline-names"}).text
    #print(company_names)
     company_names_list.append(company_names)

    #Link til flight
     link_to_flights = inner_grid.find("div", {"class": "col col-best"})
     link_to_flights = link_to_flights.find('a')['href']

     base_url = "https://kayak.dk"
     scrapped_url = base_url + link_to_flights
     flight_url = scrapped_url.replace("amp;", "")
     flight_urls.append(flight_url)

    # flight departure, stops, time ...
     flights = inner_grid.find(
        "ol", {"class": "flights"})
     both_schedules = flights.findAll("div", {"class": "section times"})
     both_section_stops = flights.findAll("div", {"class": "section stops"})
     both_durations = flights.find_all(
         "div", {"class": "section duration allow-multi-modal-icons"})

     for i in range(2):
         if i == 0:
             #Flying interval (first flight)
             first_flight_times = both_schedules[i].find(
                 "div", {"class": "top"})
             out_time = first_flight_times.text.replace('\n', '')
             print('out time: ' + out_time)
             out_time_list.append(out_time)
 
             out_stop = both_section_stops[i].text.replace('\n', '')
             print(out_stop)
             out_stops.append(out_stop)

             out_duration = both_durations[i].text.replace('\n', '')
             print(out_duration)
             out_durations.append(out_duration)
 
             #time hardcoded for now
             out_dates.append('14 juli')

         if i == 1:
             #Flying interval (second flight)
             first_flight_times = both_schedules[i].find(
                 "div", {"class": "top"})
             return_time = first_flight_times.text.replace('\n', '')
             print('return time: ' + return_time)
             return_time_list.append(return_time)
 
             return_stop = both_section_stops[i].text.replace('\n', '')
             print(return_stop)
             return_stops.append(return_stop)

             return_duration = both_durations[i].text.replace('\n', '')
             print(return_duration)
             return_durations.append(return_duration)
 
            #time date hardcoded for now
             return_dates.append('25 juli')
   cols = (['Out Date', 'Return Date', 'Out Duration',
            'Return Duration', 'Out Stops', 'Return Stops', 'Out Time', 'Return Time', 'Company names', 'Price', 'Url'])

   flights_df = pd.DataFrame({
      'Out Date': out_dates,
      'Return Date': return_dates,
      'Out Duration': out_durations,
      'Return Duration': return_durations,
      'Out Stops': out_stops,
      'Return Stops': return_stops,
      'Out Time': out_time_list,
      'Return Time': return_time_list,
      'Company names': company_names_list,
      'Price': prices,
      'Url': flight_urls})[cols]

   email_df = flights_df[flights_df["Price"] ==
                        flights_df["Price"]].nsmallest(5, 'Price')

  # so we can know when it was scraped
  #flights_df['timestamp'] = strftime("%Y%m%d-%H%M")

   subject = "Flights to Cypern"
   msg = email_df.to_html()

   CLIENT_SECRET_FILE = 'client_secret.json'
   API_NAME = 'gmail'
   API_VERSION = 'v1'
   SCOPES = ['https://mail.google.com/']
   service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

   mimeMessage = MIMEMultipart()
   mimeMessage['to'] = config.EMAIL_ADDRESS
   mimeMessage['subject'] = subject
   mimeMessage.attach(MIMEText(msg, 'html'))
   raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

   message = service.users().messages().send(
      userId='me', body={'raw': raw_string}).execute()
   print(message)

   return email_df


#63cy = hele cypern
#118cy = hele italien
final_df = srape_flights('CPH', 'LCA', '2022-07-11',
                         '2022-07-20-flexible-2days')
print(final_df)


# Load more results to maximize the scraping


def load_more(driver):
    try:
        more_results = '//a[@class = "moreButton"]'
        driver.find_element_by_xpath(more_results).click()
        print('sleeping.....')
        sleep(randint(25, 35))
    except:
        pass


def send_email(subject, msg):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.PASSWORD)
        message = 'Subject: {}\n\n{}'.format(subject, msg)
        server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, message)
        server.quit()
        print("Success: Email sent!")
    except:
        print("Email failed to send.")
