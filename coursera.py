import random
import requests
import sys
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd


def get_random_courses_list(url, courses_amount):
    xml_request = requests.get(url)
    root = etree.XML(xml_request.content)
    courses_list = [link.text for child in root for link in child]
    return random.sample(courses_list, courses_amount)


def get_course_info(course_link):
    course_request = requests.get(course_link)
    soup = BeautifulSoup(course_request.content, 'html.parser')
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
    return {
        "title": title,
        "language": language,
        "date_begin": date_begin,
        "weeks_count": weeks_count,
        "ratings": ratings
    }


def output_courses_info_to_xlsx(courses_list, filepath='courses.xlsx'):
    courses_table = pd.DataFrame(
        courses_list,
        columns=[
            'title',
            'language',
            'date_begin',
            'weeks_count',
            'ratings',
        ]
    )
    courses_table = courses_table.set_index('title')

    writer = pd.ExcelWriter(filepath)
    courses_table.to_excel(writer, 'Courses')
    writer.save()


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

    courses_list = []
    for course_link in courses_links:
        courses_list.append(get_course_info(course_link))

    output_courses_info_to_xlsx(courses_list, filepath)
