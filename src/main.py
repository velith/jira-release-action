import logging
import os
import requests

API_TOKEN  = "TOKEN"
PROJECT    = "JIRA_PROJECT_KEY"
VERSION    = "JIRA_VERSION"
HOSTNAME   = "JIRA_HOSTNAME"

def _check_env_vars(vars):
  for var in vars:
    if not os.environ[var]:
      logging.exception(f"Required env var '{var}' not set")
      exit(1)

def _get_version_id():
  jira_host = os.environ[HOSTNAME]
  project_key = os.environ[PROJECT]
  version_name = os.environ[VERSION]

  url = f"https://{jira_host}/rest/api/2/project/{project_key}/versions?expand=name,id"

  headers = {
    "Authorization": f"Bearer {os.environ[API_TOKEN]}"
  }

  versions = requests.get(url, headers=headers).json()

  for version in versions:
    if version["name"] == version_name:
      return version["id"]

  return None

def _update_version(version_id, release_version):
  jira_host = os.environ[HOSTNAME]
  project_key = os.environ[PROJECT]

  url = f"https://{jira_host}/rest/api/2/version/{version_id}"
  
  headers = {
    "Authorization": f"Bearer {os.environ[API_TOKEN]}"
  }

  payload = {
    "name":f"{release_version}",
    "released": True
  }

  return requests.put(url, 
                      headers=headers,
                      data=payload
                      ).json()

def _release_version(version_id):
  _update_version(version_id, os.environ[VERSION])

def main(request):
  _check_env_vars([API_TOKEN, PROJECT, VERSION, HOSTNAME])

  version_id = _get_version_id()

  if version_id:
    if os.environ[JIRA_RELEASE_VERSION]:
      _update_version(version_id, os.environ[JIRA_RELEASE_VERSION])
    else:
      _release_version(version_id)
  else:
    logging.info("No version updated or released")

if __name__ == "__main__":
    main(None)