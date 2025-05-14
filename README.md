# combine-contributors

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

See [combine_contributors.ipynb](combine_contributors.ipynb) as a starting place but there may be better ways to approach this

### Oops, does it already exist?

See here: [merge-all-contributors](https://github.com/openclimatefix/merge-all-contributors) but finding it a bit hard to use. Installed node via https://nodejs.org/en/download/. 

Do we build on this or make something new? It would be good to validate the outputs.

---

> add to this repo eventually: license, contribution guidelines etc. 




