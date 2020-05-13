from lib import requests
from workflow import Workflow, ICON_ERROR, ICON_WARNING, ICON_INFO, PasswordNotFound
from workflow.background import run_in_background, is_running
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
  except PasswordNotFound:
    wf.add_item("No API token found.", "Please use codatoken to set your Coda API token.", valid=False, icon=ICON_WARNING)
    wf.send_feedback()
    return 0

  res = wf.cached_data('docs', None, max_age=0)

  if (not wf.cached_data_fresh('docs', max_age=60)):
    cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
    run_in_background('update', cmd)

  log.debug(res)

  if (res):
    if (res["items"] != []):
      for item in res["items"]:
        wf.add_item(item["name"], item["browserLink"], valid=True, arg=item["browserLink"], icon="icons/doc.png")
    else: 
      wf.add_item("No documents found", icon=ICON_WARNING, valid=False)
  
  else:
    wf.add_item("Cache is being populated.", "Please run the workflow again to see results.", valid=False, icon=ICON_INFO)

  wf.send_feedback()
  return 0

if (__name__ == "__main__"):
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))
