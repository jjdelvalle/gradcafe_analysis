import sys
import requests
import asyncio
import aiohttp
import time

from pathlib import Path

url_form = "http://thegradcafe.com/survey/index.php"
params = {}
params['pp'] = 250
params['t'] = 'a'
params['o'] = 'd'
DATA_DIR = './data/'

async def scrape(sess, url, params, page):
  async with sess.get(url=url, params=params) as response:
    contents = None
    try:
      contents = await response.text()
    except Exception as e:
      print("Unable to decode using utf8")

    if contents is None:
      try:
        contents = await response.text('latin-1')
      except Exception as e:
        print("Unable to decode using latin-1")

    if contents is None:
      contents = ''

  fname = "{data_dir}{query}/{page}.html".format(
    query=params['q'],
    data_dir=DATA_DIR,
    page=str(page)
  )

  with open(fname, 'w') as f:
    f.write(contents)
  print("getting {0}...".format(page))

async def bound_fetch(semaphore, sess, url, params, page):
  async with semaphore:
    await scrape(sess, url, params, page)

async def main(urls: dict):
  params['q'] = ' '.join(sys.argv[1:-1])
  Path("{data_dir}{query}".format(data_dir=DATA_DIR, query=params['q'])).mkdir(parents=True, exist_ok=True)
  semaphore = asyncio.Semaphore(5)
  async with aiohttp.ClientSession() as sess:
    await asyncio.gather(*[bound_fetch(semaphore, sess, url, params, page) for page, url in urls.items()])

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print("Specify query and number of pages to be scraped")
    exit()

  if not sys.argv[-1].isdigit():
    print("Number of pages must be number")
    exit()

  urls = {}
  for i in range(1, int(sys.argv[-1]) + 1):
    urls[i] = url_form + "?p=" + str(i)

  start = time.time()
  asyncio.run(main(urls))
  end = time.time()
  print("It took {} seconds to scrape gradcafe.".format(end-start))
