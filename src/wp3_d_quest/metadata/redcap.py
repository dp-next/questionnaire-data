import re
from itertools import groupby
from operator import itemgetter
from typing import Any, Literal, cast

import seedcase_soil as so
import seedcase_sprout as sp


def create_package_properties(metadata: list[dict[str, Any]]) -> sp.SproutProperties:
    """Create package properties from the REDCap metadata."""
    return sp.SproutProperties.from_default(
        name="wp3-d-quest",
        title="Questionnaire data package for Work Package 3 of the DP-Next project",
        description=(
            "This repository contains the source raw data and Python code to build the "
            "data package for the DP-Next work package 3 population questionnaire. "
            "Only metadata and documentation are publicly accessible."
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
        ],
        licenses=[
            sp.LicenseProperties(
                name="CC0-1.0",
                path="https://creativecommons.org/publicdomain/zero/1.0/",
                title="CC0 1.0 Universal",
            ),
        ],
        resources=_create_resource_properties(metadata),
    )


def _create_resource_properties(
    redcap_fields: list[dict[str, str]],
) -> list[sp.ResourceProperties]:
    # Discard the participant_id field, which is added to each resource separately.
    redcap_fields = so.keep(
        redcap_fields, lambda field: field["field_name"] != "participant_id"
    )
    sorted_by_form = sorted(redcap_fields, key=lambda field: field["form_name"])
    grouped_by_form = groupby(sorted_by_form, key=lambda field: field["form_name"])
    return so.fmap(
        grouped_by_form,
        lambda group: _form_to_resource(group[0], list(group[1])),
    )


def _form_to_resource(
    form_name: str, fields: list[dict[str, str]]
) -> sp.ResourceProperties:
    participant_id_field = sp.FieldProperties(
        name="participant_id",
        title="The unique ID of the participant",
        type="string",
        description="The unique ID of the participant.",
        constraints=sp.ConstraintsProperties(required=True),
    )

    # Discard fields displayed for information only and checkbox fields,
    # which are processed separately.
    form_redcap_fields = so.keep(
        fields, lambda field: field["field_type"] not in ["descriptive", "checkbox"]
    )
    form_fields = so.fmap(
        form_redcap_fields,
        lambda field: sp.FieldProperties(
            name=field["field_name"],
            title=field["field_name"],
            type=_get_type(field),
            format=_get_format(field),
            description=_get_description(field),
            categories=_get_categories(field),
            constraints=sp.ConstraintsProperties(
                required=_get_required(field),
                enum=_get_categories(field),
                minimum=_get_validation_bound(field, "text_validation_min"),
                maximum=_get_validation_bound(field, "text_validation_max"),
                min_length=_get_text_length_bound(field, "text_validation_min"),
                max_length=_get_text_length_bound(field, "text_validation_max"),
            ),
        ),
    )

    checkbox_redcap_fields = so.keep(
        fields, lambda field: field["field_type"] == "checkbox"
    )
    checkbox_fields = so.flat_fmap(checkbox_redcap_fields, _expand_checkbox_field)

    return sp.ResourceProperties(
        name=form_name,
        # TODO: fill in title and description
        title=form_name,
        description=form_name,
        schema=sp.TableSchemaProperties(
            primary_key=["participant_id"],
            fields=[participant_id_field] + form_fields + checkbox_fields,
        ),
    )


def _expand_checkbox_field(checkbox_field: dict[str, str]) -> list[sp.FieldProperties]:
    return so.fmap(
        _get_choices(checkbox_field),
        lambda choice: sp.FieldProperties(
            name=f"{checkbox_field['field_name']}___{choice[0]}",
            title=choice[1],
            type="boolean",
            description=_get_description(checkbox_field),
            constraints=sp.ConstraintsProperties(
                required=_get_required(checkbox_field),
            ),
        ),
    )


def _get_choices(field: dict[str, str]) -> list[tuple[str, str]]:
    """Parses the choices into the choice number and choice value.

    E.g.:
        Input: "1, first choice|2, second choice|3, third choice"
        Output: [('1', 'first choice'), ('2', 'second choice'), ('3', 'third choice')]
    """
    choices = field["select_choices_or_calculations"].split("|")
    matches = so.fmap(
        choices, lambda choice: re.match(r"^(\d+), *(.*)", choice.strip())
    )
    if not all(matches):
        raise ValueError(_get_error_message(field, "select_choices_or_calculations"))
    return so.fmap(
        cast(list[re.Match[str]], matches),
        lambda match: (match.group(1), match.group(2)),
    )


def _get_required(redcap_field: dict[str, str]) -> bool:
    match redcap_field["required_field"]:
        case "y":
            return True
        case "":
            return False
        case _:
            raise NotImplementedError(
                _get_error_message(redcap_field, "required_field")
            )


def _get_description(redcap_field: dict[str, str]) -> str:
    description = redcap_field["field_annotation"]

    # Remove action tags of the form @tag, @tag(...), or @tag="..."
    # re.DOTALL makes . match newlines as well, which can also appear inside brackets.
    description = re.sub(
        r'@[\w-]+((\(.*?\))|(\s*=\s*".*?"))?', "", description, flags=re.DOTALL
    ).strip()

    if redcap_field["field_type"] == "calc":
        description += (
            " Derived using the formula: "
            + redcap_field["select_choices_or_calculations"]
        )

    if redcap_field["field_type"] == "slider":
        description += (
            f" Question: {redcap_field['field_label']}. Slider scale labels: "
            # Given as: left label | middle label | right label
            + redcap_field["select_choices_or_calculations"]
        )

    return description.strip()


def _get_categories(redcap_field: dict[str, str]) -> list[str] | None:
    if redcap_field["field_type"] not in {"radio", "dropdown"}:
        return None

    return so.fmap(_get_choices(redcap_field), itemgetter(1))


def _get_format(redcap_field: dict[str, str]) -> str | None:
    match _get_mask(redcap_field):
        case "email":
            return "email"
        case "time":
            return "%H:%M"
        case "date_ymd":
            return "%Y/%m/%d"
        case "date_mdy":
            return "%m/%d/%Y"
        case "date_dmy":
            return "%d/%m/%Y"
        case "datetime_dmy":
            return "%d/%m/%Y %H:%M"
        case "datetime_seconds_dmy":
            return "%d/%m/%Y %H:%M:%S"
        case _:
            return None


def _get_validation_bound(
    redcap_field: dict[str, str],
    field_name: Literal["text_validation_min", "text_validation_max"],
) -> float | str | None:
    value = redcap_field[field_name]
    if value == "":
        return None

    match _get_mask(redcap_field):
        case "integer":
            return int(value)
        case "number":
            return float(value)
        case (
            "number_comma_decimal"
            | "number_1dp_comma_decimal"
            | "number_2dp_comma_decimal"
        ):
            return float(value.replace(",", "."))
        case (
            "date_ymd"
            | "date_mdy"
            | "date_dmy"
            | "datetime_dmy"
            | "datetime_seconds_dmy"
            | "time"
        ):
            return value
        case _:
            return None


def _get_text_length_bound(
    redcap_field: dict[str, str],
    field_name: Literal["text_validation_min", "text_validation_max"],
) -> int | None:
    value = redcap_field[field_name]
    if value == "":
        return None

    if _get_mask(redcap_field) in {
        "",
        "email",
        "alpha_only",
        "dk_cpr_dash",
        "cpr_med_bindestreg",
    }:
        return int(value)

    return None


def _get_type(redcap_field: dict[str, str]) -> sp.FieldType:
    match redcap_field["field_type"]:
        case "text":
            return _get_type_from_mask(redcap_field)
        case "calc" | "radio" | "dropdown" | "notes" | "file":
            return "string"
        case "slider":
            return "integer"
        case _:
            raise NotImplementedError(_get_error_message(redcap_field, "field_type"))


def _get_type_from_mask(redcap_field: dict[str, str]) -> sp.FieldType:
    match _get_mask(redcap_field):
        case "" | "email" | "alpha_only" | "dk_cpr_dash" | "cpr_med_bindestreg":
            return "string"
        case (
            "number"
            | "number_comma_decimal"
            | "number_1dp_comma_decimal"
            | "number_2dp_comma_decimal"
        ):
            return "number"
        case "integer":
            return "integer"
        case "date_ymd" | "date_dmy" | "date_mdy":
            return "date"
        case "datetime_dmy" | "datetime_seconds_dmy":
            return "datetime"
        case "time":
            return "time"
        case _:
            raise NotImplementedError(
                _get_error_message(
                    redcap_field, "text_validation_type_or_show_slider_number"
                )
            )


def _get_mask(redcap_field: dict[str, str]) -> str:
    # Sliders can only hold integers regardless of the value of
    # text_validation_type_or_show_slider_number
    if redcap_field["field_type"] == "slider":
        return "integer"
    return redcap_field["text_validation_type_or_show_slider_number"]


def _get_error_message(field: dict[str, str], key: str) -> str:
    return (
        f"Unexpected value {field[key]!r} for `{key}` in field {field['field_name']!r} "
        f"in form {field['form_name']!r}."
    )
