import time

from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .utils import element_has_css_class

import os
os.environ['WDM_LOG_LEVEL'] = '0'


class TestBatonMenuMobile(TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=chrome_options,
        )
        self.driver.set_window_size(480, 600)
        self.driver.implicitly_wait(10)
        self.login()

    def tearDown(self):
        self.driver.quit()

    def login(self):
        self.driver.get('http://localhost:8000/admin')
        username_field = self.driver.find_element_by_id("id_username")
        password_field = self.driver.find_element_by_id("id_password")
        button = self.driver.find_element_by_css_selector('input[type=submit]')

        username_field.send_keys('admin')
        time.sleep(1)
        password_field.send_keys('admin')
        time.sleep(1)
        button.click()

    # selenium sees the navbar as visible because it's just moved to the left,
    # we cannot use is_displayed method
    def navbar_is_invisible(self, navbar):
        left = int(navbar.value_of_css_property('left').replace('px', ''))
        width = int(navbar.value_of_css_property('width').replace('px', ''))
        return left + width <= 0

    def navbar_is_visible(self, navbar):
        left = int(navbar.value_of_css_property('left').replace('px', ''))
        return left == 0

    def test_menu(self):
        # Wait until baton is ready
        wait = WebDriverWait(self.driver, 10)
        wait.until(element_has_css_class((By.TAG_NAME, 'body'), "baton-ready"))
        time.sleep(2)
        navbar = self.driver.find_element_by_class_name('sidebar-menu')
        self.assertEqual('menu-open' in self.driver.find_element_by_tag_name('body').get_attribute('class').split(), False)
        self.assertEqual(self.navbar_is_invisible(navbar), True)

        toggler = self.driver.find_element_by_css_selector(".navbar-toggler")
        toggler.click()
        self.assertEqual(self.navbar_is_visible(navbar), True)
        self.assertEqual('menu-open' in self.driver.find_element_by_tag_name('body').get_attribute('class').split(), True)
        root_voices = navbar.find_elements_by_css_selector('.depth-0 > li')

        close_button = self.driver.find_element_by_class_name('fa-times')
        close_button.click()
        self.assertEqual('menu-open' in self.driver.find_element_by_tag_name('body').get_attribute('class').split(), False)
        self.assertEqual(self.navbar_is_invisible(navbar), True)

        toggler.click()

        # system title voice
        self.assertEqual(root_voices[0].get_attribute('innerText'), 'SYSTEM')
        self.assertEqual(root_voices[0].is_displayed(), True)
        self.assertEqual('title' in root_voices[0].get_attribute('class').split(), True)
        self.assertEqual(len(root_voices), 4)
