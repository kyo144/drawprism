import os
import requests
from bs4 import BeautifulSoup
from models.nickname import insert_new_nicknames


def crawl_animal_name():
  url = os.getenv('CRAWL_ANIMAL_NAME_URL')
  headers = {
      'user-agent': os.getenv('CRAWL_ANIMAL_NAME_AGENT'),
      'cookie': os.getenv('CRAWL_ANIMAL_NAME_COOKIE')
  }
  res = requests.get(url, headers=headers).text
  soup = BeautifulSoup(res, 'html.parser').select('div.wordlist-item')
  words = []
  for item in soup:
    childTag = item.find('a')
    if childTag:
      if len(childTag.contents[0].split()) <= 1:
        words.append({'word': childTag.contents[0].lower()})
    else:
      if len(item.contents[0].split()) <= 1:
        words.append({'word': item.contents[0].lower()})
  insert_new_nicknames(words)
