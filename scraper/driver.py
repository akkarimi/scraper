# -*- coding: utf-8 -*-
#
# This file is part of scraper.
# Copyright 2018-2019 Leonardo Rossi <leonardo.rossi@studenti.unipr.it>.
#
# pysenslog is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pysenslog is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pysenslog.  If not, see <http://www.gnu.org/licenses/>.

"""Driver."""

import time

from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver


def scroll(driver, times=10):
    for i in range(0, times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
    return driver


def goto_end_page(driver, is_ended):
    page = driver.find_element_by_tag_name('body')
    while not is_ended():
        page.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
    return driver


class load(object):
    def __init__(self, url=None, reload_every=1000):
        self._reload_every = reload_every
        self._count_opened_urls = 0
        self.driver = webdriver.Firefox()
        if url:
            self.driver.base_url = url
            self.driver.get(self.driver.base_url)
        self.driver.implicitly_wait(2)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.quit()

    def get(self, url):
        if self._need_reload():
            self.driver.quit()
            self.driver = webdriver.Firefox()
        self.driver.base_url = url
        self.driver.get(self.driver.base_url)

    def _need_reload(self):
        # update internal counter
        self._count_opened_urls += 1
        # check if need a reset
        need = self._count_opened_urls > self._reload_every
        # if need reset, then reset also the counter
        if need:
            self._count_opened_urls = 0
        return need
