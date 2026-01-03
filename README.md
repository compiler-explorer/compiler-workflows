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

## For trusted compiler authors

If you build and administrate a branch of a compiler, then you can ask
to be added to the "External Compiler Devs" team on GitHub. This will
give you write permissions to this repo which will let you trigger your
compiler's build _and_ trigger a deploy too. There's more mischief you
could get up to too: so we will only add trusted, known accounts to this
team.

Contact Matt directly by email, or on Discord to be added to the group.

### Triggering your own compiler's build

1. Head to https://github.com/compiler-explorer/compiler-workflows/actions
2. Look for your build on the left hand pane. You may have to click
   "Show more workflows..." a few times
3. Choose your build (you can bookmark this page for ease of return later)
4. Choose "Run workflow" at the top right of the pane with prior builds
5. Choose the green "Run workflow"
6. After a pause of a few seconds your build should appear at the top of the list
7. It may take a few minutes to get scheduled, but you should then be able to
   watch it build. If it _builds quickly_ then check the output: we try not to
   build if we think there has been no changes. Check you pushed your compiler's
   changes if not, else contact the admins on Discord
8. Ensure everything goes green
9. Trigger a installation

### Triggering an installation

1. Head to https://github.com/compiler-explorer/compiler-workflows/actions/workflows/install-compilers.yml
2. Click "Run workflow"
3. Type in the build type and name, e.g. `clang hana-clang-trunk`
4. If today's build has already deployed and you want to force, tick "Force install"
5. Click "Run workflow"
6. Check it completes OK _and_ that the end of the output of the "install" / "install compilers" step looks something like:

```
2026-01-03 20:20:32,446 compilers/c++/nightly/clang hana-clang-trunk WARNING  Not running on admin node - not saving compiler version info to AWS
2026-01-03 20:20:32,446 lib.ce_install  INFO     compilers/c++/nightly/clang hana-clang-trunk installed OK
Installing compilers/c++/nightly/clang hana-clang-trunk
1 packages installed OK, 0 skipped, and 0 failed installation
```

(the warning is fine, the in-compiler explorer version number may not update until the next build, though I may fix this).

The new version should be immediately available on the live site.

### Using `gh`

You can script these, if you download and setup the `gh` Github tool. Then you can do something like:

```
gh workflow run -R compiler-explorer/compiler-workflows \
    'Install compiler(s)' \
    -f compilers='clang hana-clang-trunk' \
    -f force=true
```

Where you can change the `compilers=` line appropriately.
