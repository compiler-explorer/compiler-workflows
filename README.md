# Compiler Workflows

A place to hang Github workflow files to do our compiler builds.

## Requirements

* Python3
* curl
* jq

## Usage

It's not recommended to change files through the github website.

Instead do following:

* Clone/fork this repo and make sure you have the requirements
* Add a compiler to `compilers.yaml`
* Run `make build-yamls` (or let the pre-commit hook run this)
* Commit `compilers.yaml` and the automatically generated files
