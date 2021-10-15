import os
import sys
import urllib
from time import sleep

import pydub
import speech_recognition as sr

from colorama import Fore, Style
from random import choice, uniform

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ParserPack import Parser
from WebDriverPack.patch import webdriver_folder_name, download_latest_chromedriver
from user_agent import generate_user_agent


class ElementHasCssClass(object):
    """An expectation for checking that an element has a particular css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self, locator: tuple[webdriver.common.by.By, str], css_class: str):
        self.locator = locator
        self.css_class = css_class

    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Finding the referenced element
        if self.css_class in element.get_attribute("class"):
            return element
        else:
            return False


class WebDriver(Parser):
    __number = 0

    def __new__(cls, *args, **kwargs):
        cls.__number += 1
        return super(WebDriver, cls).__new__(cls)

    def __init__(self, marker: str = None, user_agent: bool = True, proxy: bool = False,
                 delay_time: int = 3, headless: bool = False, max_retry: int = 5):
        super(WebDriver, self).__init__()
        print(Fore.YELLOW + '[INFO]', Fore.MAGENTA + f' {marker}')
        self._user_agent = user_agent
        self._proxy = proxy
        self._delay_time = delay_time
        self._headless = headless
        self._max_retry = max_retry
        self._driver = self._get_driver()

    def __del__(self):
        self._driver.quit()

    @property
    def current_url(self):
        return self._driver.current_url

    @property
    def driver(self):
        return self._driver

    def _get_proxy(self):
        if len(self._proxies_list) == 0:
            return None
        proxy = self._current_proxy
        while proxy == self._current_proxy:
            proxy = choice(self._proxies)
        self._proxies.remove(proxy)
        self._current_proxy = proxy
        if len(self._proxies) == 0:
            self._proxies = [proxy for proxy in self._proxies_list]
        return proxy

    def _get_driver(self):
        if not os.path.exists('C:/Program Files/Google/Chrome/Application/chrome.exe'):
            sys.exit(
                "[ERR] Please make sure Chrome browser is installed "
                "(path is exists: C:/Program Files/Google/Chrome/Application/chrome.exe) "
                "and updated and rerun program"
            )
        # download latest chromedriver, please ensure that your chrome is up to date
        driver = None
        while True:
            try:
                # create chrome driver
                path_to_chromedriver = os.path.normpath(
                    os.path.join(os.getcwd() + '/WebDriverPack', webdriver_folder_name, "chromedriver.exe")
                )
                options = webdriver.ChromeOptions()
                options.headless = self._headless
                if self._user_agent:
                    if len(self._user_agents_list) > 0:
                        u_agent = choice(self._user_agents_list)
                    else:
                        u_agent = generate_user_agent()
                    print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" user-agent: {u_agent}")
                    options.add_argument('user-agent=' + u_agent)
                if self._proxy and len(self._proxies_list) > 0:
                    prx = self._get_proxy()
                    print('driver proxy: ', prx)
                    options.add_argument('--proxy-server=' + prx)
                driver = webdriver.Chrome(path_to_chromedriver, options=options)
                self.__delay(driver, self._delay_time)
                return driver
            except Exception as e:
                print(Fore.MAGENTA + '[EXCEPT]', Style.RESET_ALL +
                      f' in WebDriver._get_driver(): ', str(e))
                # patch chromedriver if not available or outdated
                if driver is None:
                    is_patched = download_latest_chromedriver()
                else:
                    is_patched = download_latest_chromedriver(
                        driver.capabilities["version"]
                    )
                if not is_patched:
                    sys.exit(
                        "[ERR] Please update the chromedriver.exe in the webdriver folder "
                        "according to your chrome version: https://chromedriver.chromium.org/downloads"
                    )

    def _reset_driver(self):
        self._driver.quit()
        self._driver = self._get_driver()

    def change_proxy(self, proxy: str = None):
        if proxy is None:
            proxy = self._get_proxy()
        prx = {
            "proxyType": "MANUAL",
            "httpProxy": proxy,
            "sslProxy": proxy
        }
        cap = webdriver.DesiredCapabilities.CHROME.copy()
        cap['proxy'] = prx
        self._driver.delete_all_cookies()
        self._driver.start_session(cap)

    @classmethod
    def __delay(cls, driver, waiting_time=3):
        driver.implicitly_wait(waiting_time)

    def get_page(self, url: str, el_max_wait_time: float = 3, element: tuple[webdriver.common.by.By, str] = None,
                 el_has_css_class: tuple[tuple[webdriver.common.by.By, str], str] = None,
                 form_data: list[list[tuple[webdriver.common.by.By, str], str]] = None,
                 recaptcha: bool = False, recaptcha_type: str = 'v2',
                 recaptcha_image_element: tuple[webdriver.common.by.By, str] = None,
                 submit_button: tuple[webdriver.common.by.By, str] = None,
                 submit_check_element: list[tuple[webdriver.common.by.By, str], str] = None):
        """Get web page by url.
        element: tuple[By, str];
        el_has_css_class: tuple[element[By, str], class];
        form_data: list[input data[element[By, 'str'], text], ...];
        recaptcha_image_element: tuple[By, str];
        submit_button: tuple[By, str];
        submit_check_element: list[element[By, str], partial_text];
        """

        for i in range(self._max_retry):
            try:
                sleep(uniform(.5, 3))
                self._driver.get(url)
                print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' driver current url: {self._driver.current_url}')

                # page element waiting
                wait = WebDriverWait(self._driver, el_max_wait_time)
                if element:
                    element = wait.until(EC.presence_of_element_located(element))
                elif el_has_css_class:
                    element = wait.until(ElementHasCssClass(el_has_css_class[0], el_has_css_class[1]))

                # form input
                if form_data:
                    self._form_input(form_data)
                    if not recaptcha:
                        self._submit_bt_click(submit_button)
                        # form submit check
                        if not submit_check_element:
                            print(Fore.YELLOW + '[INFO]', Fore.MAGENTA +
                                  'Form or recaptcha submission is determined by a change in the url, set the '
                                  'validation element if the url does not change as a result of the submission, '
                                  '\nor for better identification!')
                        if (submit_check_element and self._check_element(submit_check_element, el_max_wait_time)) \
                                or self._driver.current_url != url:
                            print(Fore.YELLOW + '[INFO]  Form submit check:', Fore.CYAN + f" passed")
                            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" Form data is submitted")
                        else:
                            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" failed to confirm the data submission")
                            print(Fore.YELLOW + '[INFO]  Form submit check:', Fore.CYAN + f" not passed")

                # recaptcha
                solved = False
                if recaptcha and ('www.google.com/recaptcha/api2' in self._driver.current_url
                                  or recaptcha_type == 'v2'):
                    solved = self.recaptcha_v2_solver(submit_button, submit_check_element)
                elif recaptcha and recaptcha_type == 'v3':
                    solved = self.recaptcha_v3_solver()
                elif recaptcha and recaptcha_type == 'image':
                    solved = self.recaptcha_image_solver(recaptcha_image_element)
                return not recaptcha or solved
            except Exception as e:
                print(Fore.MAGENTA + '[EXCEPT]', Style.RESET_ALL +
                      f' in WebDriver.get_page(): \n', str(e))
                self._reset_driver()
        return False

    def _form_input(self, data: list[list[tuple[webdriver.common.by.By, str], str]]):
        """fills in all form fields"""
        print(Fore.YELLOW + '[INFO]  _form_input')
        if data is None:
            return
        for inp_data in data:
            sleep(uniform(1.0, 5.0))
            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' form input: {inp_data[0][1]}' + Fore.CYAN + ' true')
            element = self._driver.find_element(*inp_data[0])
            offset = self._get_element_offset(element)
            action = webdriver.ActionChains(self._driver)
            action.move_to_element_with_offset(element, offset['x'], offset['y']).pause(uniform(1.0, 2.0)) \
                .send_keys_to_element(element, *inp_data[1]).perform()

    def _check_element(self, element_data: list[tuple[webdriver.common.by.By, str], str], el_max_wait_time: float = 3):
        """check if an element exists on the page"""
        element = element_data[0]
        text = element_data[1]
        try:
            wait = WebDriverWait(self._driver, el_max_wait_time)
            wait.until(EC.presence_of_element_located(element))
            if text and text not in self._driver.find_element(*element).text:
                return False
        except Exception as e:
            print(Fore.MAGENTA + '[ERROR]', Style.RESET_ALL + f"in _check_element() - Element not find. \n - {str(e)}")
            return False
        return True

    def get_element(self, element: tuple[webdriver.common.by.By, str]):
        if self._driver.current_url == 'data:,':
            return None
        return self._driver.find_element(*element)

    @classmethod
    def _get_element_offset(cls, element):
        """Set offset of the specified element.
        Offsets are relative to the top-left corner of the element.

        returned {'x': x_offset, 'y': y_offset}"""

        x_offset = uniform(element.size['width'] * .1, element.size['width'] * .9)
        y_offset = uniform(element.size['height'] * .1, element.size['height'] * .9)
        return {'x': x_offset, 'y': y_offset}

    def _submit_bt_click(self, submit):
        try:
            self._driver.switch_to.default_content()
            sleep(uniform(1.0, 5.0))
            element = self._driver.find_element(*submit)
            offset = self._get_element_offset(element)
            action = webdriver.ActionChains(self._driver)
            action.move_to_element_with_offset(element, offset['x'], offset['y']) \
                .pause(uniform(1.0, 2.0)).click().perform()
        except Exception as e:
            print(Fore.MAGENTA + '[EXCEPT]', Style.RESET_ALL +
                  f' in WebDriver._submit_bt_click(self, submit): recaptcha submit not find, '
                  f'\n{str(e)}')

    def recaptcha_v2_solver(self, submit: tuple[webdriver.common.by.By, str] = None,
                            submit_check_element: list[tuple[webdriver.common.by.By, str], str] = None):
        print(Fore.YELLOW + '[INFO]  recaptcha_v2_solver')
        start_url = self._driver.current_url
        recaptcha_control_frame = None
        recaptcha_challenge_frame = None
        for i in range(2):
            # find recaptcha frames
            sleep(uniform(1.0, 5.0))
            frames = self._driver.find_elements_by_tag_name("iframe")
            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' iframes count: {len(frames)}')
            for index, frame in enumerate(frames):
                if frame.get_attribute("title") == "reCAPTCHA":
                    recaptcha_control_frame = frame
                if frame.get_attribute("title") == "проверка recaptcha":
                    recaptcha_challenge_frame = frame
            if not recaptcha_control_frame or not recaptcha_challenge_frame:
                print(Fore.MAGENTA + '[ERR]', Style.RESET_ALL + " Unable to find recaptcha.")
                if submit and i == 0:
                    self._submit_bt_click(submit)
                else:
                    # form submit check
                    if not submit_check_element:
                        print(Fore.YELLOW + '[INFO]', Fore.MAGENTA +
                              'Form or recaptcha submission is determined by a change in the url, set the validation '
                              'element if the url does not change as a result of the submission, \nor for better '
                              'identification!')
                    if (submit_check_element and self._check_element(submit_check_element)) \
                            or self._driver.current_url != start_url:
                        print(Fore.YELLOW + '[INFO]  Submit check:', Fore.CYAN + f" passed")
                        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" data is submitted")
                        return True
                    else:
                        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" failed to confirm the data submission")
                        print(Fore.YELLOW + '[INFO]  Submit check:', Fore.CYAN + f" not passed")
                    print(Fore.YELLOW + '[INFO]', Fore.CYAN + " Abort solver.")
                    raise ValueError('raise exception to reset driver.')
            else:
                break

        # switch to recaptcha frame
        self._driver.find_elements_by_tag_name("iframe")
        self._driver.switch_to.frame(recaptcha_control_frame)

        # click on checkbox to activate recaptcha
        sleep(uniform(1.0, 5.0))
        element = self._driver.find_element_by_class_name("recaptcha-checkbox-border")
        offset = self._get_element_offset(element)
        action = webdriver.ActionChains(self._driver)
        action.move_to_element_with_offset(element, offset['x'], offset['y']) \
            .pause(uniform(1.0, 2.0)).click().perform()
        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' recaptcha-checkbox is clicked')
        sleep(3)
        if 'display: none' in element.get_attribute('style'):
            print(Fore.YELLOW + '[INFO]  Recaptcha pass check: ' + Fore.CYAN + 'passed')
            if submit:
                self._submit_bt_click(submit)
                # form submit check
                if not submit_check_element:
                    print(Fore.YELLOW + '[INFO]', Fore.MAGENTA +
                          'Form or recaptcha submission is determined by a change in the url, set the validation '
                          'element if the url does not change as a result of the submission, \nor for better '
                          'identification!')
                if (submit_check_element and self._check_element(submit_check_element)) \
                        or self._driver.current_url != start_url:
                    print(Fore.YELLOW + '[INFO]  Submit check:', Fore.CYAN + f" passed")
                    print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" data is submitted")
                else:
                    print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" failed to confirm the data submission")
                    print(Fore.YELLOW + '[INFO]  Submit check:', Fore.CYAN + f" not passed")
            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" Recaptcha is passed")
            return True

        # switch to recaptcha audio control frame
        self._driver.switch_to.default_content()
        self._driver.find_elements_by_tag_name("iframe")
        self._driver.switch_to.frame(recaptcha_challenge_frame)

        # click on audio challenge
        sleep(uniform(1.0, 5.0))
        element = self._driver.find_element_by_id("recaptcha-audio-button")
        offset = self._get_element_offset(element)
        action = webdriver.ActionChains(self._driver)
        action.move_to_element_with_offset(element, offset['x'], offset['y']). \
            pause(uniform(1.0, 2.0)).click().perform()
        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' recaptcha-audio-button is clicked')

        # switch to recaptcha audio challenge frame
        self._driver.switch_to.default_content()
        self._driver.find_elements_by_tag_name("iframe")
        self._driver.switch_to.frame(recaptcha_challenge_frame)

        for i in range(5):
            # get the mp3 audio file
            sleep(uniform(1.0, 5.0))
            src = self._driver.find_element_by_id("audio-source").get_attribute("src")
            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" Audio src: {src}")

            path_to_mp3 = os.path.normpath(os.path.join(os.getcwd(), "WebDriverPack/sample.mp3"))
            path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "WebDriverPack/sample.wav"))

            # download the mp3 audio file from the source
            urllib.request.urlretrieve(src, path_to_mp3)

            # load downloaded mp3 audio file as .wav
            try:
                # as administrator program run required
                sound = pydub.AudioSegment.from_mp3(path_to_mp3)
                sound.export(path_to_wav, format="wav")
                sample_audio = sr.AudioFile(path_to_wav)
            except Exception as e:
                print(Fore.MAGENTA + '[EXCEPT]', Style.RESET_ALL +
                      f' in WebDriver.recaptcha_v2_solver(): \n{str(e)}')
                sys.exit(
                    "[ERR] Please run program as administrator or download ffmpeg manually, "
                    "https://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/"
                )

            # translate audio to text with google voice recognition
            r = sr.Recognizer()
            with sample_audio as source:
                audio = r.record(source)
            key = r.recognize_google(audio)
            print(Fore.YELLOW + '[INFO]', f" Recaptcha Passcode:" + Fore.CYAN + f" {key}")

            # key in results and submit
            sleep(uniform(1.0, 5.0))
            element = self._driver.find_element_by_id("audio-response")
            offset = self._get_element_offset(element)
            action = webdriver.ActionChains(self._driver)
            action.move_to_element_with_offset(element, offset['x'], offset['y']).pause(uniform(1.0, 2.0)) \
                .send_keys_to_element(element, key.lower()).send_keys_to_element(element, Keys.ENTER).perform()
            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' Recaptcha Passcode is send')

            # check if recaptcha is passed
            sleep(3)
            src_ = self._driver.find_element_by_id("audio-source").get_attribute("src")
            err_ = self._driver.find_element_by_class_name('rc-audiochallenge-error-message')
            if err_.text.strip() == '' or src_ == src:
                print(Fore.YELLOW + '[INFO]  Recaptcha pass check: ' + Fore.CYAN + 'passed')

                # submit recaptcha result
                if submit:
                    self._submit_bt_click(submit)
                    # form submit check
                    if not submit_check_element:
                        print(Fore.YELLOW + '[INFO]', Fore.MAGENTA +
                              'Form or recaptcha submission is determined by a change in the url, set the validation '
                              'element if the url does not change as a result of the submission, \nor for better '
                              'identification!')
                    if (submit_check_element and self._check_element(submit_check_element)) \
                            or self._driver.current_url != start_url:
                        print(Fore.YELLOW + '[INFO]  Submit check:', Fore.CYAN + f" passed")
                        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" data is submitted")
                    else:
                        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" failed to confirm the data submission")
                        print(Fore.YELLOW + '[INFO]  Submit check:', Fore.CYAN + f" not passed")
                print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" Recaptcha is passed")
                return True
            else:
                print(Fore.YELLOW + '[INFO]', Fore.MAGENTA +
                      f' audio-error-message: {err_.text}\n' +
                      Fore.YELLOW + '[INFO]  Pass check: ' + Fore.CYAN + 'not passed, re-listening')
        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" Recaptcha is not passed")
        return False

    def recaptcha_v3_solver(self):
        # TODO: add service integration fore pass v3 recaptcha
        return False

    def recaptcha_image_solver(self, recaptcha_image: tuple[webdriver.common.by.By, str] = None):
        # TODO: add service integration fore pass image recaptcha
        return False
