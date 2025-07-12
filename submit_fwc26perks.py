import sys
import time
import logging
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from apscheduler.schedulers.blocking import BlockingScheduler

# Form data
FORM_DATA = {
    'first': 'Peter',
    'last': 'Kennedy',
    'email': 'pkennedy5421@gmail.com',
    'confirm_email': 'pkennedy5421@gmail.com',
    'postal_code': '07003',
    'state': 'NJ',
    'advantage': '06B9FF6',
}

# Logging setup
LOG_FILE = 'submit_fwc26perks.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
)

def log(msg, level='info'):
    print(msg)
    if level == 'error':
        logging.error(msg)
    else:
        logging.info(msg)

# Email notification on error
EMAIL_TO = 'pkennedy5421@gmail.com'
EMAIL_FROM = 'pkennedy5421@gmail.com'  # Use your real sending email
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'pkennedy5421@gmail.com'  # Use your real sending email
SMTP_PASS = 'YOUR_APP_PASSWORD'  # Use an app password or real password

def send_error_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        log(f"Error email sent to {EMAIL_TO}")
    except Exception as e:
        log(f"Failed to send error email: {e}", level='error')

# URL
URL = 'https://www.fwc26perks.com/'

def submit_form(test_mode=False):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(URL)
        log('Loaded main page.')

        wait = WebDriverWait(driver, 30)
        # Look for the first iframe on the page
        try:
            iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
            iframe_url = iframe.get_attribute('src')
            log(f'IFrame URL found: {iframe_url}')
        except Exception as e:
            log(f'No iframe found or error: {e}', level='error')
            send_error_email('FWC26Perks Script Error: No iframe found', str(e))
            driver.quit()
            return

        # Drop the first driver
        driver.quit()
        time.sleep(1)

        # Create a new driver for the iframe URL
        driver2 = webdriver.Chrome(options=chrome_options)
        driver2.get(iframe_url)
        log('Loaded iframe URL.')
        wait2 = WebDriverWait(driver2, 30)

        if test_mode:
            log('TEST MODE: Printing iframe page source for inspection...')
            time.sleep(5)
            with open('iframe_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver2.page_source)
            log('Iframe page source saved to iframe_page_source.html. Please inspect this file for field names/selectors.')
            #driver2.quit()
            #return

        # Wait for the form to load (update selector as needed)
        element =  wait2.until(EC.presence_of_element_located((By.ID, 'root')))
        time.sleep(10)
        try:
           # print(element.text)
           # print(driver2.find_element(By.TAG_NAME, 'form').text)
            driver2.find_element(By.ID, 'first').send_keys(FORM_DATA['first'])
           # print(driver2.find_element(By.ID, 'first').text)
            driver2.find_element(By.ID, 'last').send_keys(FORM_DATA['last'])
            driver2.find_element(By.ID, 'email').send_keys(FORM_DATA['email'])
            driver2.find_element(By.ID, 'confirmEmail').send_keys(FORM_DATA['confirm_email'])
            driver2.find_element(By.ID, 'zip').send_keys(FORM_DATA['postal_code'])
            # Do NOT fill 'state' (disabled)
            driver2.find_element(By.ID, 'aaNumber').send_keys(FORM_DATA['advantage'])

            # Check the checkboxes by ID
            for checkbox_id in ['confirmAge', 'agreeRules', 'agreeToAaMarketing']:
                checkbox = driver2.find_element(By.ID, checkbox_id)
                if not checkbox.is_selected():
                    checkbox.click()

            # Find the submit button
            submit_btn = driver2.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            if test_mode:
                log('TEST MODE: Form filled but not submitted.')
            else:
                submit_btn.click()
                log('Form submitted.')
        except Exception as e:
            log(f'Error filling or submitting the form: {e}', level='error')
            send_error_email('FWC26Perks Script Error: Form Submission', str(e))
        driver2.quit()
    except Exception as e:
        log(f'Critical error in script: {e}', level='error')
        send_error_email('FWC26Perks Script Error: Critical', str(e))

def schedule_job():
    scheduler = BlockingScheduler()
    scheduler.add_job(submit_form, 'cron', hour=17, minute=0)
    log('Scheduled job to run every day at 5pm.')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].upper() == 'TEST':
        log('Running in TEST mode: will print iframe URL and save iframe page source.')
        submit_form(test_mode=True)
        log('Test complete.')
    else:
        log('Submitting form now and scheduling daily run at 5pm...')
        submit_form()
        # Uncomment the next line to enable daily scheduling
        # schedule_job() 