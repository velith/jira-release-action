# Jira Release Action

Github action for making a Jira release. For inputs provide project key and version to be released. You can optionally provide a change to the version name.

## Usage

A common usage can be to tag a version then make a release in Jira for the same verison.

```yaml
name: 'Jira GitHub Actions'
on:
  - push
jobs:
  release:
    name: 'Jira Release'
    runs-on: ubuntu-latest
    steps:
      - name: 'Checkout'
        uses: actions/checkout@master
      - name. 'Release App'
        ## Make a release
      - name: 'Tag version'
        ## Tag version control
      - name: 'Jira release'
        uses: velith/jira-release-action@v1
        with:
          jira_project_key: "MYPROJ"
          jira_version: "1.1.x"
          jira_release_version: "1.1.15"
          jira_hostname: "jira.example.com"
        env:
          TOKEN: ${{ secrets.JIRA_TOKEN }}
```

Using a placeholder version while developing and then setting the final version with this actions allows a team to accumulate issues to a version and once release is made, rename the version to match the version of the app. All this automatically.

## Inputs

Inputs configure Terraform GitHub Actions to perform different actions.

* `jira_project_key` - (Required) Project key in Jira.
* `jira_version` - (Required) Version to be released.
* `jira_hostanme` - (Required) Hostname of the Jira software.
* `jira_release_version` - (Optional) A new name for the version to be released.

## Outputs

There are no outputs of this action.
