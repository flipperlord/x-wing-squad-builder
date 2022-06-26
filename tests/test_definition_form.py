import pytest
from x_wing_squad_builder.definition_form import DefinitionForm


@pytest.fixture(scope="module")
def definition_form(definition_file_path):
    return DefinitionForm(definition_file_path)
