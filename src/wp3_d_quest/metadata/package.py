import seedcase_sprout as sp

package_properties = sp.SproutProperties(
    name="wp3-d-quest",
    title="Questionnaire data package for Work Package 3 of the DP-Next project",
    description=(
        "This repository contains the source raw data and Python code to build the "
        "data package for the DP-Next work package 3 population questionnaire. "
        "This package contains the data and metadata from a questionnaire sent out to "
        "residents in Denmark who had an HbA1c measurement taken in the last 24 months "
        "and who are between 40-50 years of age. The questionnaire study is part of "
        "the DP-Next project. Only metadata and documentation are publicly accessible, "
        "personal data is kept within GenomeDK."
    ),
    homepage="https://dp-next.github.io/wp3-d-quest",
    contributors=[
        sp.ContributorProperties(
            title="Kristiane Beicher",
            email="kris.beicher@clin.au.dk",
            given_name="Kristiane",
            family_name="Beicher",
            organization="Steno Diabetes Centre Aarhus",
            roles=["DataManager", "DataCurator", "ContactPerson"],
        ),
        sp.ContributorProperties(
            title="Signe Kirk Brødbæk",
            email="signekb@clin.au.dk",
            given_name="Signe Kirk",
            family_name="Brødbæk",
            organization="Steno Diabetes Centre Aarhus",
            roles=["DataManager", "DataCurator"],
        ),
        sp.ContributorProperties(
            title="Luke W Johnston",
            email="lwjohnst@clin.au.dk",
            given_name="Luke",
            family_name="Johnston",
            organization="Steno Diabetes Centre Aarhus",
            roles=["DataManager", "DataCurator"],
        ),
        sp.ContributorProperties(
            title="Marton Vago",
            email="mvago@clin.au.dk",
            given_name="Marton",
            family_name="Vago",
            organization="Steno Diabetes Centre Aarhus",
            roles=["DataManager", "DataCurator"],
        ),
        # TODO: Add other contributors, like David, Kristina, etc.
    ],
    licenses=[
        sp.LicenseProperties(
            name="CC0-1.0",
            path="https://creativecommons.org/publicdomain/zero/1.0/",
            title="CC0 1.0 Universal",
        ),
    ],
    id="0b14e351-79ee-4790-a3d5-ba087e38b24f",
    version="0.1.0",
    created="2026-09-08T16:35:37+02:00",
)
