# All All Contributors

*All Contributors at the level of a GitHub Organisation*

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg?style=flat-square)](#contributors-) <!-- ALL-CONTRIBUTORS-BADGE:END -->
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

## Introduction and project goals

Many communities that host their work on GitHub use the [All Contributor](https://allcontributors.org) specification for

> "recognizing contributors to an open-source project in a way that rewards every contribution, not just code", https://allcontributors.org/docs/en/overview

There is a bot that helps a community use this specification in an automated way:

> "The bot will automatically pull a user's profile, grab the contribution type emoji, update the project README and then open a Pull Request against the project ✨", https://allcontributors.org/docs/en/tooling

This bot works well, but it only works at the level of a repository, not an organisation. When an organisation has multiple repositories, there is a need to capture all contributors (and their contribution types) at the level of the organisation.

This project will provide a way to fetch all of the `.all-contributorsrc` files from each repo contained with an organisation. Once fetched, it will combine them together and summarise each contributor and all of their unique contributions.

## Usage

### Inputs

| Input Name | Input Description | Required? |
| :--- | :--- | :--- |
| `organisation` | The name of the GitHub organisation to collect all-contributors from | **YES** |
| `target_repo` | The name of the repository within the GitHub organisation where the merged all-contributors file will live | **YES** |
| `github_token` | A GitHub token with permissions to write to the contents of the target repo and open pull requests. Defaults to: `GITHUB_TOKEN`. | no |
| `target_filepath` | Path to a plain text file containing a list of repos within the organisation to exclude from the merge. Defaults to: `.repoignore`. | no |
| `base_branch` | The name of the branch on the target repo to open pull requests against. Defaults to: `main`. | no |
| `head_branch` | A prefix to prepend to head branches when opening pull requests. Defaults to: `merge-all-contributors`. | no |

### Permissions

This Action will need permission to read the contents of a files stored in repositories in an organisation, create a new branch, commit to that branch, and open a Pull Request.
The [default permissive settings of `GITHUB_TOKEN`](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token) should provide the relevant permissions.

If instead your repository is using the default restricted settings of `GITHUB_TOKEN`, you could grant just enough permissions to the Action using a [`permissions`](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions#jobsjob_idpermissions) config, such as the one below:

```yaml
permissions:
  contents: write
  pull-requests: write
```

## Contributors ✨

This project started at the [2025 SSI Collaboration Workshop Hack Day](https://www.software.ac.uk/workshop/collaborations-workshop-2025-cw25).

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://blog.jmadge.com"><img src="https://avatars.githubusercontent.com/u/23616154?v=4?s=100" width="100px;" alt="Jim Madge"/><br /><sub><b>Jim Madge</b></sub></a><br /><a href="https://github.com/the-turing-way/all-all-contributors/commits?author=JimMadge" title="Code">💻</a> <a href="#ideas-JimMadge" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=JimMadge" title="Tests">⚠️</a> <a href="#infra-JimMadge" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://nikosirmpilatze.com"><img src="https://avatars.githubusercontent.com/u/20923448?v=4?s=100" width="100px;" alt="Niko Sirmpilatze"/><br /><sub><b>Niko Sirmpilatze</b></sub></a><br /><a href="#ideas-niksirbi" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=niksirbi" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://thomaszwagerman.co.uk/"><img src="https://avatars.githubusercontent.com/u/36264706?v=4?s=100" width="100px;" alt="Thomas Zwagerman"/><br /><sub><b>Thomas Zwagerman</b></sub></a><br /><a href="#ideas-thomaszwagerman" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=thomaszwagerman" title="Code">💻</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=thomaszwagerman" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/RayStick"><img src="https://avatars.githubusercontent.com/u/50215726?v=4?s=100" width="100px;" alt="Rachael Stickland"/><br /><sub><b>Rachael Stickland</b></sub></a><br /><a href="#ideas-RayStick" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=RayStick" title="Code">💻</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=RayStick" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://sgibson91.github.io/"><img src="https://avatars.githubusercontent.com/u/44771837?v=4?s=100" width="100px;" alt="Sarah Gibson"/><br /><sub><b>Sarah Gibson</b></sub></a><br /><a href="#ideas-sgibson91" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=sgibson91" title="Code">💻</a> <a href="#infra-sgibson91" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=sgibson91" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/akbanana7"><img src="https://avatars.githubusercontent.com/u/116113592?v=4?s=100" width="100px;" alt="Akram Karoune"/><br /><sub><b>Akram Karoune</b></sub></a><br /><a href="#ideas-akbanana7" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=akbanana7" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Sahil590"><img src="https://avatars.githubusercontent.com/u/56438860?v=4?s=100" width="100px;" alt="Sahil Raja"/><br /><sub><b>Sahil Raja</b></sub></a><br /><a href="#ideas-Sahil590" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/the-turing-way/all-all-contributors/commits?author=Sahil590" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
