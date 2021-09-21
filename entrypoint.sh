#!/usr/bin/env bash

if [ -n "${INPUT_JIRA_PROJECT_KEY}" ]; then
  export JIRA_PROJECT_KEY="${INPUT_JIRA_PROJECT_KEY}"
else
  echo "Input jira_project_key cannot be empty"
  exit 1
fi

if [ -n "${INPUT_JIRA_HOSTNAME}" ]; then
  export JIRA_HOSTNAME="${INPUT_JIRA_HOSTNAME}"
else
  echo "Input jira_hostname cannot be empty"
  exit 1
fi

if [ -n "${INPUT_JIRA_VERSION}" ]; then
  export JIRA_VERSION="${INPUT_JIRA_VERSION}"
else
  echo "Input jira_version cannot be empty"
  exit 1
fi

if [ -z "${TOKEN}" ]; then
  echo "env TOKEN cannot be empty"
  exit 1
fi

if [ -n "${INPUT_JIRA_RELEASE_VERSION}" ]; then
  export JIRA_RELEASE_VERSION="${INPUT_JIRA_RELEASE_VERSION}"
fi

if [ -n "${INPUT_JIRA_TRANSITION_ID}" ]; then
  export JIRA_TRANSITION_ID="${INPUT_JIRA_TRANSITION_ID}"
fi

if [ -n "${INPUT_JIRA_STATUS_NAME}" ]; then
  export JIRA_STATUS_NAME="${INPUT_JIRA_STATUS_NAME}"
fi


scriptDir=$(dirname ${0})
output=$(python ${scriptDir}/main.py ${*} 2>&1)
exitCode=${?}

echo "${output}"
exit ${exitCode}