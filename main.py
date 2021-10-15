# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from random import choice
from time import sleep

from colorama import Fore, Style
from selenium.webdriver.common.by import By

from WebDriverPack.webDriver import WebDriver, Parser

# Press the green button in the gutter to run the script.

if __name__ == '__main__':
    driver = WebDriver('login to acc')

    # form_data = [
    #     [(By.ID, 'mail-name'), 'Alex'],
    #     [(By.ID, 'mail-email'), 'email@info.com'],
    #     [(By.ID, 'mail-message'), 'something very interesting'],
    # ]
    # page = driver.get_page('https://gorgames.ru/contacts/', el_max_wait_time=10,
    #                        form_data=form_data,
    #                        submit_check_element=[(By.CSS_SELECTOR, 'body'), 'Сообщение успешно отправлено'],
    #                        submit_button=(By.CSS_SELECTOR, '#root > div.page > div.contacts.content-block > form > div > div > div:nth-child(2) > input'))
    # print('done ', page)
    # sleep(5)

    # page = driver.get_page('https://www.google.com/recaptcha/api2/demo', el_max_wait_time=10,
    #                        submit_check_element=[(By.CSS_SELECTOR, 'body div'), 'Проверка прошла успешно'],
    #                        recaptcha=True,
    #                        submit_button=(By.ID, 'recaptcha-demo-submit'))
    # print('done ', page)
    # sleep(5)

    form_data = [
        [(By.ID, 'signin-login'), 'gorod1974@hotmail.com'],
        [(By.ID, 'signin-password'), 'katapulta'],
    ]
    page = driver.get_page('https://rsocks.net/signin', el_max_wait_time=10,
                           form_data=form_data,
                           submit_check_element=[(By.CSS_SELECTOR, '#wrapper nav div.left-menu__user-info div:nth-child('
                                                               '1) span:nth-child(2)'), None],
                           recaptcha=True,
                           submit_button=(By.CSS_SELECTOR, '#formSignin div.row div:nth-child(1) > button'))
    print('done ', page)
    sleep(5)

    # page = driver.get_page('https://antcpt.com/rus/information/demo-form/recaptcha-3-test-score.html')
    # for i in range(30):
    #     page = driver.get_page('https://www.google.com/recaptcha/api2/demo',
    #                            recaptcha_submit=(By.ID, 'recaptcha-demo-submit'))
    # page = driver.get_page('https://gorgames.ru', 5.5, element=(By.ID, 'left'))
    # if page:
    #     html = driver.get_element((By.ID, 'left')).get_attribute('innerHTML')
    #     print(html)

    # inp = None
    # while inp != 'y':
    #     inp = input('tape "y" for continue: ')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
