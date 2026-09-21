# Contributing

## :bug: Issues and bugs

The easiest way to contribute is to report issues or bugs that you might find
while using questionnaire-data. You can do this by creating a new issue on our
GitHub repository.

## :pencil2: Adding or modifying content

If you would like to contribute content, please check out our
[guidebook](https://guidebook.seedcase-project.org/) for more specific details
on how we work and develop. It is a regularly evolving document, so is at
various states of completion.

To contribute to questionnaire-data, you first need to install
[uv](https://docs.astral.sh/uv/) and
[justfile](https://just.systems/man/en/packages.html). We use uv and justfile to
manage our project, such as to run checks on the data package and build the
website. Both the uv and justfile websites have a more detailed guide on using
uv, but below are some simple instructions to get you started.

It's easiest to first [install
uv](https://docs.astral.sh/uv/getting-started/installation/) and then install
justfile with uv. Once you've installed uv, install justfile by running:

```bash
uv tool install rust-just
```

We keep all our development workflows in the `justfile`, so you can explore it
to see what commands are available. To see a list of commands available, run:

```bash
just
```

You can run a recipe by typing:

```bash
just <recipe-name>
```

As you contribute, make sure your changes will pass our checks by opening a
terminal so that the working directory is the root of this project
(`questionnaire-data/`) and running our recipes. Some recipes to run regularly
are:

```bash
just check-all
just build-package
```

Which runs some checks (like formatting and code checks) and builds the data
package (like regenerating the `datapackage.json` file).

And once you're ready to create a pull request, you run:

```bash
just run-all
```

When committing changes, please try to follow [Conventional
Commits](https://decisions.seedcase-project.org/why-conventional-commits/) as
Git messages. Using this convention allows us to be able to automatically create
a release based on the commit message by using
[Cocogitto](https://decisions.seedcase-project.org/why-semantic-release-with-cocogitto/).
If you don't use Conventional Commits when making a commit, we will revise the
pull request title to follow that format, as we use squash merges when merging
pull requests, so all other commits in the pull request will be squashed into
one commit.

## :file_folder: Explanation of files and folders

This is a brief description of some of the files in this repository.

### Data package content

- `src/`: The folder you should put all your Python files in, as this data
  package is structured like a Python package. The organization of the folder is
  up to you, but we recommend following a structure commonly found in data
  engineering projects, e.g. in
  [dbt](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview?version=2)
  projects. We recommend that Python files only contain functions and classes
  for data processing, while the actual data processing is done in `main.py` to
  keep all the processing steps in one place.
  - Use the naming convention
    `src/questionnaire_data/<data-source>/<data-resource>_(data|metadata).py`
    for your Python files. `data-source` is the source that your data comes from
    (see `raw/` below) and `data-resource` is the name of the (eventual) data
    resource.
  - Utility or common functions should be kept in a
    `src/questionnaire_data/common/` folder.
- `raw/`: The folder for all your raw data files. These data files should come
  directly from their source locations (e.g. a database, an API, or a downloaded
  file) without having been modified in any way. Name the files using the
  convention: `raw/<data-source>/<timestamp>.csv` (or whatever format your data
  is in).
- `staging/`: The folder where processed data files are stored after they've
  been tidied from `raw/` but before they've been converted into a resource in
  `resources/`. The files in this folder can be used to actually create the
  resource properties, as they will all be in a tidy format with their data
  types and values more or less in their final form. Name the files using the
  convention: `staging/<data-source>/<data-resource>/<timestamp>.parquet`
  (Sprout requires Parquet).
- `resources/`: The folder with your data resources. Each resource has its own
  Parquet file (or files) containing all resource data contained within.

### Configuration and other content

- `.copier-answers.yml`: Contains the answers you gave when copying the project
  from the template. **You should not modify this file directly.**
- `.github/`: Contains GitHub-specific files, such as issue and pull request
  templates, workflows,
  [dependabot](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/dependabot-quickstart-guide)
  configuration, pull request templates, and a
  [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
  file.
- `_quarto.yml`: Quarto configuration file for the website, including settings
  for the website, such as the theme, navigation, and other options.
- `_metadata.yml`: Quarto metadata file for the website, including information
  about the project, such as the titles and GitHub names.
- `.gitignore`: This ignore file tells Git which files to not track. Unless you
  know what you are doing, it's best to not touch this file.
- `.pre-commit-config.yaml`: [Pre-commit](https://pre-commit.com/) configuration
  file for managing and running checks before each commit.
- `.config/`: Contains configuration files for various tools used in the
  project, such as:
  - `typos.toml`: [typos](https://github.com/crate-ci/typos) spell checker
    configuration file.
  - `rumdl.toml`: [rumdl](https://rumdl.dev) configuration file for formatting
    Markdown files in the project.
  - `cog.toml`: [Cocogitto](https://docs.cocogitto.io) configuration file for
    managing versions.
  - `lychee.toml`: [Lychee](https://lychee.cli.rs) configuration file for
    checking URLs.
  - `cliff.toml`: [git-cliff](https://git-cliff.org) configuration file for
    creating the changelog.
  - `ruff.toml`: [Ruff](https://github.com/charliermarsh/ruff) configuration
    file for linting and formatting Python code.
- `.editorconfig`: Editor configuration file for
  [EditorConfig](https://editorconfig.org/) to maintain consistent coding styles
  across different editors and IDEs.
- `CITATION.cff`: Structured citation metadata for your project when archived on
  [Zenodo](https://zenodo.org/) and used by GitHub to display the citation
  information on the repository page. This is used to add the metadata to Zenodo
  when a GitHub release has been uploaded to Zenodo.
- `justfile`: [`just`](https://just.systems/man/en/) configuration file for
  scripting project tasks.
- `CHANGELOG.md`: Changelog file for tracking changes in the project.

## Developing your data package

The first steps for creating and developing your data package are kept in the
`src/questionnaire-data/build.py`. For more detailed instructions on developing
data packages, check out the [Building Data
Packages](https://data-pkg-guide.seedcase-project.org) guide.
