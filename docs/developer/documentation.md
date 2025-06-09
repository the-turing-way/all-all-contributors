# Documentation Guide

The documentation is built using [mkdocs](https://www.mkdocs.org/). We use [mkdocstrings](https://mkdocstrings.github.io/) and [mkdocs-autoapi](https://mkdocs-autoapi.readthedocs.io/en/latest/) to automatically generate the API references.

### Building the Docs
To preview the documentation locally:
```console
hatch run docs:serve
```

To build the documentation:
```console
hatch run docs:build
```

### Navigation
The navigation is handled in `mkdocs.yml`:
```yaml
nav:
  - Overview: index.md
  - Developer Guide:
    - Documentation: developer/documentation.md
  - License: license.md
```
The pages listed here can be edited manually.

Note that the API section (which is not listed under `nav:`) is automatically generated using `mkdocstrings` and `mkdocs-autoapi`, when you call `mkdocs serve`.

This is because we use the following configuration in `mkdocs.yml`:
```yaml
plugins:
  - search
  - mkdocs-autoapi:
      autoapi_add_nav_entry: API
  - mkdocstrings:
      handlers:
        python:
          paths:
            - .
          options:
            show_submodules: true
            docstring_style: google
            heading_level: 3
```

Therefore, there is no need to create or edit `.md` files when you make a change to the code under `all_all_contributors/`. Do make sure you update the docstrings if needed.

### Docstrings Style
For the docstrings, please follow the [Google Style Guide][https://google.github.io/styleguide/pyguide.html#383-functions-and-methods]. For more information on `mkdocstrings`, see their [Docstring Options][https://mkdocstrings.github.io/python/usage/configuration/docstrings/].
