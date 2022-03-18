from cmath import log
import json
import logging
import os
import requests

from datetime import date

API_TOKEN       = "TOKEN"
PROJECT         = "JIRA_PROJECT_KEY"
VERSION         = "JIRA_VERSION"
HOSTNAME        = "JIRA_HOSTNAME"
RELEASE_VERSION = "JIRA_RELEASE_VERSION"
TRANSITION_ID   = "JIRA_TRANSITION_ID"
STATUS_NAME     = "JIRA_STATUS_NAME"

def _check_env_vars(vars):
  for var in vars:
    if not os.environ.get(var):
      logging.exception(f"Required env var '{var}' not set")
      exit(1)

def _get_version_id():
  jira_host = os.environ.get(HOSTNAME)
  project_key = os.environ.get(PROJECT)
  version_name = os.environ.get(VERSION)

  url = f"https://{jira_host}/rest/api/2/project/{project_key}/versions?expand=name,id"

  headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}"
  }

  versions = requests.get(url, headers=headers).json()

  for version in versions:
    if version["name"] == version_name:
      return version["id"]

  logging.info(f"No version found in project {project_key} with name ${version_name}")
  return None

def _close_issues(version):
  if not (os.environ.get(STATUS_NAME) and os.environ.get(TRANSITION_ID)):
    logging.info("Status name and/or transition not provided. Not updating any Jira issues.")
    return ""

  jira_host = os.environ.get(HOSTNAME)
  project_key = os.environ.get(PROJECT)
  status = os.environ.get(STATUS_NAME)

  headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}",
    "Accept": "application/json",
    "Content-Type": "application/json"
  }

  url = f"https://{jira_host}/rest/api/2/search"

  query = {
    "jql": f"project = {project_key} AND status = '{status}' AND fixVersion = {version}",
    "fields": "id"
  }

  issue_search = requests.get(
    url,
    headers=headers,
    params=query
  ).json()

  if not issue_search:
    logging.warning(f"No issues found for '{project_key}' with status '{status}' and version '{version}'")
    exit(0)

  logging.info(f"Found {len(issue_search['issues'])} issues")

  payload = json.dumps({
    "transition": {
      "id": os.environ.get(TRANSITION_ID)
    }
  })

  for issue in issue_search["issues"]:
    url = f"https://{jira_host}/rest/api/2/issue/{issue['id']}/transitions"
    res = requests.post(
      url,
      headers=headers,
      data=payload
    )
    if res.status_code == 200:
      logging.info(f"Moved {issue['id']} to Done")
    else:
      logging.warning(f"Could not move {issue['id']} to Done")
      logging.warning(json.loads(res.text))

def _release_and_update_version(version_id, release_version):
  jira_host = os.environ.get(HOSTNAME)

  url = f"https://{jira_host}/rest/api/2/version/{version_id}"
  
  headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}",
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  today = date.today()
  releaseDate = today.strftime("%Y-%m-%d")

  payload = json.dumps({
    "name": release_version,
    "released": "true",
    "releaseDate": releaseDate
  })

  res = requests.put(url,
                  headers=headers,
                  data=payload
                  )

  if res.status_code != 200:
    logging.warning(f"Failed to update and release Jira version {release_version}")
    logging.warning(json.loads(res.text))

  return release_version

def _release_version(version_id):
  return _release_and_update_version(version_id, os.environ.get(VERSION))

def _create_new_version(version):
  jira_host = os.environ.get(HOSTNAME)

  url = f"https://{jira_host}/rest/api/2/version"

  headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}",
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  placeholder_version = f"{str(version).rsplit('.', 1)[0]}.xyz"

  payload = json.dumps({
    "name": placeholder_version,
    "project": os.environ.get(PROJECT)
  })

  res = requests.post(url, headers=headers, data=payload)
  if res.status_code != 200:
    logging.warning(f"Failed to create new placeholder verions {placeholder_version}")
    logging.warning(json.loads(res.text))

  return requests.post(url, headers=headers, data=payload)

def main(request):
  _check_env_vars([API_TOKEN, PROJECT, VERSION, HOSTNAME])

  version_id = _get_version_id()

  if version_id:
    _close_issues(os.environ.get(VERSION))
    if os.environ.get(RELEASE_VERSION):
      _release_and_update_version(version_id, os.environ.get(RELEASE_VERSION))
      _create_new_version(os.environ.get(RELEASE_VERSION))
    else:
      _release_version(version_id)
  else:
    logging.info("No version updated or released")

if __name__ == "__main__":
    main(None)