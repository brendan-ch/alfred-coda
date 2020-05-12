from lib import requests
from workflow import Workflow, ICON_ERROR, ICON_WARNING
import sys
import argparse

def main(wf):
  parser = argparse.ArgumentParser()
  
  parser.add_argument('--settoken', dest='apitoken', nargs='?', default=None)
  parser.add_argument('query', nargs='?', default=None)
  args = parser.parse_args(wf.args)

  if (args.apitoken):
    log.debug("Saving API key")
    wf.save_password('coda_token', args.apitoken)
    return 0

  try:
    log.debug("Getting API token")
    key = wf.get_password('coda_token')
  except:
    wf.add_item("No API token found.", "Please use codatoken to set your Coda API token.", valid=False)
    wf.send_feedback()
    return 0

  headers = {"Authorization": "Bearer %s" % key}
  params = {"isOwner": True}

  res = wf.cached_data('docs', max_age=120)
  if (res == None):
    try:
      res = requests.get("https://coda.io/apis/v1beta1/docs", headers=headers, params=params)
      res.raise_for_status()
      res = res.json()
      wf.cache_data('docs', res)
    except requests.exceptions.HTTPError as err:
      wf.add_item("Unsuccessful status code", "Please check your API token and try again.", valid=False, icon=ICON_ERROR)
      wf.send_feedback()
      return 0
    except requests.exceptions.ConnectionError as err:
      wf.add_item("Connection error", "Please check your network connection and try again.", valid=False, icon=ICON_ERROR)
      wf.send_feedback()
      return 0

  log.debug(res)

  if (res["items"] != []):
    for item in res["items"]:
      wf.add_item(item["name"], item["browserLink"], valid=True, arg=item["browserLink"], icon="icons/doc.png")
  else: 
    wf.add_item("No documents found", icon=ICON_WARNING, valid=False)

  wf.send_feedback()
  return 0

if (__name__ == "__main__"):
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))
