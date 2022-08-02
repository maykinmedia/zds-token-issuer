# Contributing to ZDS Token Issuer

## Reporting issues

Please report issues to the [ZDS Token Issuer][token-issuer-issues] repository.

We manage issues/bugs/userstories centralized so that they can be prioritized
by the product owner and planned into the sprint. There are templates available
for new user stories or bugs.

## Implementing features

We welcome enthusiasm for new features!

However, to prevent dissapointment, we recommend you to:

* create a user story in [ZDS Token Issuer][token-issuer-issues] - it's possible that
  the conclusion is that we don't want to support that feature (for the time
  being)

**Style guides**

* we use `isort` and `black` to make sure imports are consistently sorted (config in `setup.cfg`)
* PEP8 applies to code formatting (config in `setup.cfg`)
* The [Django code-style][django-coding-style] applies as well
* the `.editorconfig` file contains configuration per file-type. Most editors
  should pick this up automatically.

## Suggesting API changes

We welcome you to suggest changes to the API itself! Please do so by making a
pull request in [ZDS Token Issuer][token-issuer].

[token-issuer]: https://github.com/vng-Realisatie/gemma-zaken
[token-issuer-issues]: https://github.com/vng-Realisatie/gemma-zaken/issues
[django-coding-style]: https://docs.djangoproject.com/en/stable/internals/contributing/writing-code/coding-style/
