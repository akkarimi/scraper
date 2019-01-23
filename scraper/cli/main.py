# -*- coding: utf-8 -*-
#
# This file is part of scraper.
# Copyright 2019 Leonardo Rossi <leonardo.rossi@studenti.unipr.it>.
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

"""CLI main."""

import click

from pprint import pprint
from functools import partial

from .validators import get_hashtag
from ..twitter import scraper as tscraper


@click.group()
def cli():
    pass


@cli.group()
def twitter():
    pass


@twitter.command()
@click.argument('hashtag', callback=get_hashtag)
@click.option('--per_driver', '-p', default=0, type=int, show_default=True,
              help="How many times scroll for each driver")
@click.option('--times', '-t', default=1, type=int, show_default=True,
              help="How many times open a new driver")
def scrape(hashtag, per_driver, times):
    """Scrape twitter."""
    my_scraper = partial(
        tscraper.scraper, baseurl=tscraper.baseurl, per_driver=per_driver
    )
    for t in tscraper.scrape_more(
            query=tscraper.query, q=hashtag, scraper=my_scraper, times=times):
        pprint(t._info)