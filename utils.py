import logging

from bs4 import BeautifulSoup
from requests import RequestException
from pydantic import BaseModel, HttpUrl

from exceptions import ParserFindTagException


class LoggerWarning(BaseModel):
    status: str
    short_status: str
    url: HttpUrl


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_pep_status(session, url):
    status = ''
    if not url:
        return status
    response = get_response(session, url)
    pep_soup = BeautifulSoup(response.text, features='lxml')
    dl_div = find_tag(pep_soup, 'dl')
    dt_divs = BeautifulSoup.find_all(dl_div, 'dt')
    for dt_div in dt_divs:
        if dt_div.text == 'Status:':
            status = dt_div.find_next_sibling().string
            break
    return status
