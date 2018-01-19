import random
from os.path import realpath

from pyexcel_xlsxw import save_data

import requests
import sys
from lxml import etree
from bs4 import BeautifulSoup


def get_web_content(url):
    return requests.get(url).content


def get_random_courses_list(url, courses_amount):
    xml_root = etree.XML(get_web_content(url))
    courses_list = [link.text for child in xml_root for link in child]
    return random.sample(courses_list, courses_amount)


def get_course_info(course_link):
    soup = BeautifulSoup(get_web_content(course_link), 'html.parser')
    title = soup.select(
        '.rc-PhoenixCdpBanner .header-container .title'
    )[0].text
    language = soup.find('div', {'class': 'rc-Language'}).text
    date_begin = soup.find('div', {'class': 'rc-StartDateString'}).text
    weeks_count = len(soup.select(".rc-WeekView > .week"))
    ratings = soup.select('.ratings-text.bt3-hidden-xs > span')
    if ratings:
        ratings = float(ratings[0].text[-3:])
    else:
        ratings = None

    return [title, language, date_begin, weeks_count, ratings]


def output_courses_info_to_xlsx(courses_list, filepath='courses.xlsx'):
    save_data(filepath, {"Random courses": courses_list})


if __name__ == '__main__':
    courses_count = 20

    courses_links = get_random_courses_list(
        'https://www.coursera.org/sitemap~www~courses.xml',
        courses_count
    )

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = 'courses.xlsx'

    courses_list = [
        [
            'title',
            'language',
            'date_begin',
            'weeks_count',
            'ratings'
        ],
    ]
    for course_link in courses_links:
        courses_list.append(get_course_info(course_link))

    output_courses_info_to_xlsx(courses_list, filepath)
    print("Готово!\nРезультат в файле:\n{}".format(realpath(filepath)))
