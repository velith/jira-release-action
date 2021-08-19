import json
import logging
import os
import requests

API_TOKEN       = "TOKEN"
PROJECT         = "JIRA_PROJECT_KEY"
VERSION         = "JIRA_VERSION"
HOSTNAME        = "JIRA_HOSTNAME"
RELEASE_VERSION = "JIRA_RELEASE_VERSION"

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

  return None

def _close_issues(version_id):
  jira_host = os.environ.get(HOSTNAME)

  headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}",
    "Accept": "application/json",
    "Content-Type": "application/json"
  }

  url = f"https://{jira_host}/rest/api/2/search"

  query = {
    "jql": f"project = COAPP AND status = 'Ready for release' AND fixVersion = {version_id}",
    "fields": "id"
  }

  issue_search = requests.get(
    url,
    headers=headers,
    params=query
  ).json()

  payload = json.dumps({
    "transition": {
      "id": "71"
    }
  })

  for issue in issue_search["issues"]:
    url = f"https://{jira_host}/rest/api/2/issue/{issue['id']}/transitions"
    requests.post(
      url,
      headers=headers,
      data=payload
    )

def _release_and_update_version(version_id, release_version):
  jira_host = os.environ.get(HOSTNAME)

  url = f"https://{jira_host}/rest/api/2/version/{version_id}"
  
  headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}",
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  payload = json.dumps({
    "name": release_version,
    "released": True
  })

  requests.put(url, 
                  headers=headers,
                  data=payload
                  )
  return release_version

def _release_version(version_id):
  return _release_and_update_version(version_id, os.environ.get(VERSION))

def _create_new_version(version_id):
  jira_host = os.environ.get(HOSTNAME)

  url = f"https://{jira_host}/rest/api/2/version"

  headers = {
    "Authorization": f"Bearer {os.environ.get(API_TOKEN)}",
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  payload = json.dumps({
    "name": f"{version_id.rsplit('.', 1)[0]}.xyz"
  })

  return requests.post(url, headers=headers, data=payload)

def main(request):
  _check_env_vars([API_TOKEN, PROJECT, VERSION, HOSTNAME])

  version_id = _get_version_id()

  if version_id:
    _close_issues(version_id)
    if os.environ.get(RELEASE_VERSION):
      _release_and_update_version(version_id, os.environ.get(RELEASE_VERSION))
      _create_new_version(version_id)
    else:
      _release_version(version_id)
  else:
    logging.info("No version updated or released")

if __name__ == "__main__":
    main(None)