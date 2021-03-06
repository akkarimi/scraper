
"""Twitter CLI."""

import click
import json

from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from functools import partial

from ..twitter import scraper, tweet
from .. import stats as s, exc, driver as drv
from .validators import get_hashtag


@click.group()
def twitter():
    pass


@twitter.group()
def scrape():
    pass


@scrape.command()
@click.argument('hashtag', callback=get_hashtag)
@click.option('--per_driver', '-p', default=0, type=int, show_default=True,
              help="How many times scroll for each driver")
@click.option('--times', '-t', default=1, type=int, show_default=True,
              help="How many times open a new driver")
@click.option('--from-id', '-f', default=None, help="Start from this id")
@click.option('--language', '-l', default=None, help="Filter by language")
def ids(hashtag, per_driver, times, from_id, language):
    """Scrape Twitter."""
    my_scraper = partial(
        scraper.scraper, baseurl=scraper.baseurl, per_driver=per_driver
    )

    # build query
    query = deepcopy(scraper.query)
    if language:
        query['l'] = language

    try:
        for id_, username in scraper.scrape_more(
                    query=query,
                    q=hashtag,
                    scraper=my_scraper,
                    times=times,
                    max_id=from_id
                ):
            print('{0}, {1}'.format(id_, username))
    except exc.NoMoreItems:
        # no more tweets available on the timetable
        pass


@scrape.command()
@click.argument('input_', type=click.File('r'))
@click.option('--reload-every', '-r', default=1000, type=int,
              help="Reload selenium browser every X times.")
def hydrate(input_, reload_every):
    with drv.load(reload_every=reload_every) as loader:
        for value in input_:
            id_, username = value.strip().split(', ')
            try:
                t = scraper.get_tweets(
                    loader,
                    tweet.TweetFromScroll.get_url(username, id_)
                )
                print(json.dumps(t._info))
            except exc.UnknowObject:
                # if something went wrong loading page, skip
                pass


@twitter.command()
@click.argument('input_', type=click.File('r'))
@click.option('--language', '-l', default=None, help="Filter by language")
@click.option('--percentage', '-p', default=0.5,
              help="Percentage of X words to be considered X")
def stats(input_, language, percentage):
    """Show some statistics about the tweets."""
    if language:
        is_lang = s.is_of_lang(
            lang=language,
            filter_text=lambda w: not w.startswith('#'),
            percentage=percentage
        )
    count_all_posts = 0
    count_all_comments = 0
    count_posts = 0
    count_comments = 0
    count_comments_with_video = 0
    count_posts_with_video = 0
    count_retweets = 0
    count_likes = 0
    count_retweets_posts = 0
    count_likes_posts = 0
    count_without_comments = 0
    count_post_with_imgs = 0
    count_comments_with_imgs = 0
    count_without_comments = 0
    count_videos = 0
    count_imgs = 0
    users = defaultdict(lambda: 0)
    users_posting = defaultdict(lambda: 0)
    hashtags = defaultdict(lambda: 0)
    date_from = datetime.now()
    date_to = datetime.now()
    ids = []
    for line in input_:
        line = json.loads(line)
        count_all_posts += 1
        gen = tweet.iterate_tweets(line)
        post = next(gen)
        if post['id'] not in ids:
            ids.append(post['id'])
            for t in gen:
                count_all_comments += 1
                if not language or \
                        is_lang(s.remove_punctuations(t['text']).strip()):
                    count_comments += 1
                    if t['video']:
                        count_comments_with_video += 1
                        count_videos += len(t['video'])
                    users[t['username']] += 1
                    for ht in t['hashtags']:
                        # FIXME save as lower
                        hashtags[ht.lower()] += 1
                    if t['retweets']:
                        count_retweets += s.parse_humanized_int(t['retweets'])
                    if t['likes']:
                        count_likes += s.parse_humanized_int(t['likes'])
                    if t.get('image', []) != []:
                        count_comments_with_imgs += 1
                    count_imgs += len(t.get('image', []))
            if not language or \
                    is_lang(s.remove_punctuations(post['text']).strip()):
                count_posts += 1
                users_posting[line['username']] += 1
                users[post['username']] += 1
                for ht in post['hashtags']:
                    # FIXME save as lower
                    hashtags[ht.lower()] += 1
                if post['video']:
                    count_posts_with_video += 1
                    count_videos += len(post['video'])
                if post['retweets']:
                    count_retweets_posts += s.parse_humanized_int(
                        post['retweets']
                    )
                    count_retweets += s.parse_humanized_int(post['retweets'])
                if post['likes']:
                    count_likes_posts += s.parse_humanized_int(post['likes'])
                    count_likes += s.parse_humanized_int(post['likes'])
                if post['comments']['total'] == 0:
                    count_without_comments += 1
                if post.get('image', []) != []:
                    count_post_with_imgs += 1
                count_imgs += len(post.get('image', []))
                timestamp = datetime.fromtimestamp(int(post['time']))
                if date_from > timestamp:
                    date_from = timestamp
                if date_to < timestamp:
                    date_to = timestamp

    if language:
        print('language: {0}'.format(language))
    print('period of time: from {0} to {1}'.format(date_from, date_to))
    print('# users: {0}'.format(len(users.keys())))
    print('# posts: {0} of {1}'.format(count_posts, count_all_posts))
    print('# comments: {0} of {1}'.format(count_comments, count_all_comments))
    print('# comments / # post: {0:0.2f}'.format(count_comments / count_posts))
    print('# likes / # post: {0:0.2f}'.format(count_likes_posts / count_posts))
    print('# videos: {0}'.format(count_videos))
    print('# post with video: {0}'.format(count_posts_with_video))
    print('# comments with video: {0}'.format(count_comments_with_video))
    print('# images: {0}'.format(count_imgs))
    print('# tweets with images: {0}'.format(count_post_with_imgs))
    print('# comments with images: {0}'.format(count_comments_with_imgs))
    print('# users posting: {0}'.format(len(users_posting.keys())))
    print('# all likes: {0}'.format(count_likes))
    print('# post likes: {0}'.format(count_likes_posts))
    print('# all retweets: {0}'.format(count_retweets_posts))
    print('# post retweets: {0}'.format(count_retweets_posts))
    print('# posts without comments: {0}'.format(count_without_comments))
    print('# users with less than 5 posts/comments: {0}'.format(
        len(list(filter(lambda x: x < 5, users.values())))
    ))
    print('most used hashtags:')
    for ht in sorted(hashtags, key=hashtags.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(ht, hashtags[ht]))
    print('most posting users (# post):')
    for username in sorted(
            users_posting, key=users_posting.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(username, users_posting[username]))
    print('\t...')
    print('most prolific users (# post + # comments):')
    for username in sorted(users, key=users.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(username, users[username]))
    print('\t...')


@twitter.command()
@click.argument('input_', type=click.File('r'))
def hashtags(input_):
    """Get the list of hashtags and number of times it appear in a tweet."""
    hashtags = defaultdict(lambda: 0)
    for line in input_:
        line = json.loads(line)
        for post in tweet.iterate_tweets(line):
            for ht in post['hashtags']:
                # FIXME save as lower
                hashtags[ht.lower()] += 1
    for ht in sorted(hashtags, key=hashtags.__getitem__, reverse=True):
        print('{0} = {1}'.format(ht, hashtags[ht]))
