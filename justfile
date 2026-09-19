@_default:
    just --list --unsorted

# Run all build-related recipes in the justfile
run-all: install-deps update-quarto-theme format-all check-all build-all

# Run all format-related recipes
format-all: format-md format-python

# Run all check-related recipes
check-all: check-spelling check-urls check-python check-unused check-security

# Run all build-related recipes
build-all: build-contributors build-website build-readme

# List all TODO items in the repository
list-todos:
    grep -R -n \
      --exclude-dir=*_cache \
      --exclude-dir=.git \
      --exclude-dir=.quarto \
      --exclude-dir=.venv \
      --exclude-dir=_site \
      --exclude-dir=_temp \
      --exclude-dir=template \
      --exclude=copier.yaml \
      --exclude=json.code-snippets \
      --exclude=justfile \
      "TODO" .

# Install the pre-commit hooks
install-precommit:
    uvx pre-commit install
    uvx pre-commit autoupdate
    uvx pre-commit run --all-files

# Update the Quarto seedcase-theme extension
update-quarto-theme:
    # Add theme if it doesn't exist, update if it does
    quarto update dp-next/dp-next-theme --no-prompt

# Install Python package dependencies
install-deps:
    uv sync --all-extras --dev --upgrade

# Format Markdown files
format-md:
    # Use both rumdl and panache, for different purposes
    uvx rumdl fmt --silent
    uvx --from panache-cli panache format . --quiet

# Reformat Python code to match coding style and general structure
format-python:
    uvx ruff check --fix .
    uvx ruff format .

# Check for spelling errors in files
check-spelling:
    uvx typos --config .config/typos.toml

# Check Python code for any errors that need manual attention
check-python:
    uvx ruff check .
    # Check types
    uvx pyrefly check

# Run basic security checks on the package
check-security:
    uvx bandit -r src/

# Install lychee from https://lychee.cli.rs/guides/getting-started/
# Check that URLs work
check-urls:
    lychee . --config .config/lychee.toml

# Check for unused code in the package and its tests
check-unused:
    # exit code=0: No unused code was found
    # exit code=3: Unused code was found
    # Confidence value:
    # - 100 %: function/method/class argument, unreachable code
    # There are some things should be ignored though, with the allowlist.
    # Create an allowlist with `vulture --make-allowlist`
    uvx vulture --min-confidence 100 src/ **/vulture-allowlist.py

# Run the 'raw' tasks to build the raw data and/or metadata, e.g. by downloading from the source locations into `raw/`
build-raw:
    uv run pytask build -m raw

# Run the 'staging' tasks to build the files in `staging/`
build-staging:
    uv run pytask build -m staging

# Run the 'metadata' tasks to build the metadata files, e.g. `datapackage.json`
build-metadata:
    uv run pytask build -m metadata

# Build the final resources from the staging files
build-resources:
    # Requires filling out config file for Sprout.
    uxv seedcase-sprout build-resources

# Build all files for the data package, such as metadata, README, and resources
build-package version="0.0.0": build-staging build-metadata build-resources build-readme
    #!/usr/bin/env bash
    # Safer script, see https://just.systems/man/en/safer-bash-shebang-recipes.html
    set -euxo pipefail
    # Move into `releases/latest/` to make it easier to make a tar file.
    # CHANGELOG will be generated first when running `release`, see `.config/cog.toml`.
    cp --target-directory releases/latest/ \
      datapackage.json \
      LICENSE.md \
      README.md \
      CHANGELOG.md \
      resources/**/*.parquet
    repo=$(basename $(pwd))
    (
      cd releases/latest/ && \
        tar --create --file=$repo.tar * && \
        zip $repo.zip \
          datapackage.json \
          LICENSE.md \
          README.md \
          CHANGELOG.md
    )
    cp releases/latest/$repo.tar \
      releases/$repo_{{ version }}.tar
    cp releases/latest/$repo.zip \
      releases/$repo_{{ version }}.zip

# Generate a Quarto include file with the contributors
build-contributors:
    sh ./tools/get-contributors.sh dp-next/questionnaire-data > docs/includes/_contributors.qmd

# Re-build the README file from the Quarto version
build-readme:
    uv run quarto render README.qmd --to gfm

# Build the documentation for the data package
build-metadata-docs:
    uv run seedcase-flower build

# Build the documentation website using Quarto
build-website: build-metadata-docs
    uv run quarto render --execute

# Build data package and create a new release
[confirm("Are you sure you want to run the release process? (yes/no)")]
release: run-all
    #!/usr/bin/env bash
    # Safer script, see https://just.systems/man/en/safer-bash-shebang-recipes.html
    set -euxo pipefail
    # TODO: Remove once ready to release.
    echo "Release process not ready, cancelling."
    exit 0

# Preview the documentation website with automatic reload on changes
preview-website: build-metadata-docs
    uv run quarto quarto preview --execute

# Check for and apply updates from the template
update-from-template:
    # Do not update existing source files
    uvx copier update --defaults $(find src/questionnaire_data -type f -printf "--exclude %p ")

# Reset repo changes to match the template
reset-from-template:
    uvx copier recopy --defaults
