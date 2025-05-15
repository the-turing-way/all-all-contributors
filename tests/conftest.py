import json

from pytest import fixture


@fixture()
def target_all_contributors_rc():
    return """
{
  "_comment": "This JSON file controls the behaviour of the all contributors bot. A description of the keys can be found here: https://allcontributors.org/docs/en/bot/configuration",
  "files": [
    "README.md",
  ],
  "imageSize": 100,
  "contributorsPerLine": 7,
  "badgeTemplate": "[![All Contributors](https://img.shields.io/badge/all_contributors-<%= contributors.length %>-orange.svg)](#contributors)",
  "skipCi": false,
  "contributorsSortAlphabetically": true,
  "contributors": [
    {
      "login": "harrylime",
      "name": "Harry Lime",
      "avatar_url": "example.com/example.png",
      "profile": "example.com",
      "contributions": [
        "doc",
        "ideas",
        "question",
        "talk"
      ]
    },
    {
      "login": "samspade",
      "name": "Sam Spade",
      "avatar_url": "example.com/example.png",
      "profile": "example.com",
      "contributions": [
        "infra",
        "doc"
      ]
    },
  ],
  "projectName": "my-project",
  "projectOwner": "my-org",
  "repoType": "github",
  "repoHost": "https://github.com",
  "commitConvention": "none",
  "commitType": "docs"
}
"""


@fixture()
def target_all_contributors_rc_object(target_all_contributors_rc):
    return json.loads(target_all_contributors_rc)
