from workflow import Workflow, PasswordNotFound
from lib import requests
import os

def get_docs(token):
  headers = {"Authorization": "Bearer %s" % token}

  r = requests.get("https://coda.io/apis/v1beta1/docs", headers=headers)

  if (r.status_code == 401):
    wf.store_data('error', 1)
    r.raise_for_status()

  results = r.json()
  return results

def main(wf):
  try:
    token = wf.get_password('coda_token')

    def wrapper():
      return get_docs(token)

    docs = wf.cached_data('docs', wrapper, max_age=1)
    wf.logger.debug("%s docs cached" % len(docs['items']))

    filelist = []
    for f in os.listdir('icons'):
      os.remove('icons/%s' % f)  # remove existing icons in case icon was removed

    for item in docs['items']:
      try:
        icon = requests.get(item['icon']['browserLink'])

        with open("icons/%s.png" % item['id'], 'wb') as iconFile:
          iconFile.write(icon.content)
      except:
        None  # silently fail if no icon found

    wf.store_data('error', 0)

  except PasswordNotFound:
    wf.logger.error("No API token saved")

if __name__ == "__main__":
  wf = Workflow()
  wf.run(main)