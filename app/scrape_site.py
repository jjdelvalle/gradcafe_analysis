import sys
import requests
from pathlib import Path

url_form = "http://thegradcafe.com/survey/index.php"
params = {}
params['pp'] = 250
params['t'] = 'a'
params['o'] = 'd'
DATA_DIR = './data/'

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print("Specify query and number of pages to be scraped")
    exit()

  if not sys.argv[-1].isdigit():
    print("Number of pages must be number")
    exit()

  params['q'] = ' '.join(sys.argv[1:-1])
  for i in range(1, int(sys.argv[-1]) + 1):
    url = url_form
    params['p'] = i
    r = requests.get(url, params=params)
    r.encoding = 'utf-8'
    Path("{data_dir}{query}".format(data_dir=DATA_DIR, query=params['q'])).mkdir(parents=True, exist_ok=True)
    fname = "{data_dir}{query}/{page}.html".format(
      query=params['q'],
      data_dir=DATA_DIR,
      page=str(i)
    )

    with open(fname, 'w') as f:
      f.write(r.text)
    print("getting {0}...".format(i))
