# combine-contributors

### Introduction 

Many communities that host their work on GitHub use the [All Contributor](https://allcontributors.org) specification for 

> "recognizing contributors to an open-source project in a way that rewards every contribution, not just code", https://allcontributors.org/docs/en/overview

There is a bot that helps a community use this specification in an automated way:

> "The bot will automatically pull a user's profile, grab the contribution type emoji, update the project README and then open a Pull Request against the project ✨", https://allcontributors.org/docs/en/tooling

This bot works well, but it only works at the level of a repository, not an organisation. When an organisation has multiple repositories, there is a need to capture all contributors (and their contribution types) at the level of the organisation. 

## Use-case 

[The physiopy community](https://github.com/physiopy) is an organisation with multiple repositories. The [team page](https://physiopy.github.io/community/team/) on the website is out of date, and there is not an automated way to keep it up to date. This community wants an up to date picture of their contributors across the whole organisation, including all repositories. This can be used on this website, in publications/presentations and in grant applications etc. 

## Solution

See [combine_contributors.ipynb](combine_contributors.ipynb) as a starting place, but ... 

Does it already exist? 

See here: [merge-all-contributors](https://github.com/openclimatefix/merge-all-contributors) but finding it a bit hard to use. Installed node via https://nodejs.org/en/download/. 

Do we build on this or make something new? It would be good to validate the outputs.

Further enhancements:
- Validate the outputs 
- A way to edit the group contributor file without the source being an individual repo 
- How to keep it up to date 
- Render and display these organisation contributions nicely in a README  
    - See ideas at end of [combine_contributors.ipynb](combine_contributors.ipynb)
    - Would be nice to be able to sort in different ways, for example: (1) alphabetical (2) institution/affiliation/country and (3) contributor type 

> If making it public, add license and contribution guidelines etc. 




