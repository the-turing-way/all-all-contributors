# All All Contributors / All Contributors at the level of a GitHub Org
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)

### Introduction 

Many communities that host their work on GitHub use the [All Contributor](https://allcontributors.org) specification for 

> "recognizing contributors to an open-source project in a way that rewards every contribution, not just code", https://allcontributors.org/docs/en/overview

There is a bot that helps a community use this specification in an automated way:

> "The bot will automatically pull a user's profile, grab the contribution type emoji, update the project README and then open a Pull Request against the project ✨", https://allcontributors.org/docs/en/tooling

This bot works well, but it only works at the level of a repository, not an organisation. When an organisation has multiple repositories, there is a need to capture all contributors (and their contribution types) at the level of the organisation. 

## Use-case 

[The physiopy community](https://github.com/physiopy) is an organisation I am a part of. This organisation has multiple repositories. The [team page](https://physiopy.github.io/community/team/) on the website is out of date, and there is not an automated way to keep it up to date. This community wants an up to date picture of their contributors across the whole organisation, including all repositories. This can be used on this website, in publications/presentations and in grant applications etc. Maybe implement any solutions in this repo: https://github.com/physiopy/.github? (Can also be displayed in this README). 

## Potential solution

After combining across the .allcontributorsrc JSON files to create a organsiation .allcontributorsrc file, we'd want to:
1. Validate it (e.g. has it combined across all the contributors, removed any duplicate contribution tags and only kept the unique ones)
2. Render it in the organisational README with contributor names, pictures and contribution types (as done at level of repo).
3. Bonus: Other than editing it manually, would there be a way to add a contribution to this org contribution file when the source is *not* a repo contribution?
4. Bonus: How to keep it up to date? Can it trigger to update everytime a .allcontributorsrc in any repo is changed?
5. Bonus: Can we have different ways of sorting? E.g Default order, Alphabetical by author name, Contribution Type, institution/affiliation/countr (if exists)

See [combine_contributors.ipynb](combine_contributors.ipynb) as a starting place but there may be better ways to approach this. I am relatively new to APIs and GitHub Actions!

### Oops, let's not duplicate effort:

- Read this thread: https://github.com/all-contributors/all-contributors/issues/416

- See here: [merge-all-contributors](https://github.com/openclimatefix/merge-all-contributors) but finding it a bit hard to use. Installed node via https://nodejs.org/en/download/. 

---

> add to this repo eventually (if needed): license, contribution guidelines etc. 





## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://blog.jmadge.com"><img src="https://avatars.githubusercontent.com/u/23616154?v=4?s=100" width="100px;" alt="Jim Madge"/><br /><sub><b>Jim Madge</b></sub></a><br /><a href="https://github.com/RayStick/all-all-contributors/commits?author=JimMadge" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://nikosirmpilatze.com"><img src="https://avatars.githubusercontent.com/u/20923448?v=4?s=100" width="100px;" alt="Niko Sirmpilatze"/><br /><sub><b>Niko Sirmpilatze</b></sub></a><br /><a href="#ideas-niksirbi" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://thomaszwagerman.co.uk/"><img src="https://avatars.githubusercontent.com/u/36264706?v=4?s=100" width="100px;" alt="Thomas Zwagerman"/><br /><sub><b>Thomas Zwagerman</b></sub></a><br /><a href="#ideas-thomaszwagerman" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/RayStick"><img src="https://avatars.githubusercontent.com/u/50215726?v=4?s=100" width="100px;" alt="Rachael Stickland"/><br /><sub><b>Rachael Stickland</b></sub></a><br /><a href="#ideas-RayStick" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/RayStick/all-all-contributors/commits?author=RayStick" title="Code">💻</a> <a href="#projectManagement-RayStick" title="Project Management">📆</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!