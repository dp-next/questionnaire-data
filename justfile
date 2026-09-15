@_default:
    just --list --unsorted

# Run all build-related recipes in the justfile
run-all: install-deps update-quarto-theme format-python format-md check-all build-all

# Run all format-related recipes
format-all: format-md format-python

# Run all check-related recipes
check-all: check-spelling check-urls check-python check-unused check-security

# Run all build-related recipes
build-all: build-datapackage build-contributors build-website build-readme

# List all TODO items in the repository
list-todos:
  grep -R -n \
    --exclude="*.code-snippets" \
    --exclude-dir=.quarto \
    --exclude-dir=_site \
    --exclude=justfile \
    "TODO" *

# Install the pre-commit hooks
install-precommit:
  uvx pre-commit install
  uvx pre-commit autoupdate
  uvx pre-commit run --all-files
# Update the Quarto seedcase-theme extension
update-quarto-theme:
  # Add theme if it doesn't exist, update if it does
  quarto update seedcase-project/seedcase-theme --no-prompt

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
  uv run mypy --pretty .

# Run basic security checks on the package
check-security:
  uvx bandit -r src/

# Install lychee from https://lychee.cli.rs/guides/getting-started/
# Check that URLs work
check-urls:
  lychee . \
    --verbose \
    --extensions md,qmd,py \
    --exclude-path "_badges.qmd"

# Check for unused code in the package and its tests
check-unused:
  # exit code=0: No unused code was found
  # exit code=3: Unused code was found
  # Confidence value:
  # - 100 %: function/method/class argument, unreachable code
  # There are some things should be ignored though, with the allowlist.
  # Create an allowlist with `vulture --make-allowlist`
  uvx vulture --min-confidence 100 src/ **/vulture-allowlist.py

# Re-build the data package
build-datapackage:
  uv run main.py

# Generate a Quarto include file with the contributors
build-contributors:
  sh ./tools/get-contributors.sh seedcase-project/wp3-d-quest > docs/includes/_contributors.qmd

# Re-build the README file from the Quarto version
build-readme:
  uvx --from quarto quarto render README.qmd --to gfm

# Build the documentation for the data package
build-metadata-docs:
  uv run seedcase-flower build

# Build the documentation website using Quarto
build-website: build-metadata-docs
  uvx quarto render

# Preview the documentation website with automatic reload on changes
preview-website: build-metadata-docs
  uvx quarto preview

# Check for and apply updates from the template
update-from-template:
  # Do not update existing source files
  uvx copier update --defaults $(find src/wp3_d_quest -type f -printf "--exclude %p ")

# Reset repo changes to match the template
reset-from-template:
  uvx copier recopy --defaults
