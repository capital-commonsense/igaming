from pathlib import Path

import pytest

from dc_igaming.flow import FlowInputs, compute_flows
from dc_igaming.params import load_params

PARAMS_PATH = Path(__file__).resolve().parents[1] / "model" / "params.yaml"


@pytest.fixture(scope="session")
def params():
    return load_params(PARAMS_PATH)


@pytest.fixture(scope="session")
def central_inputs(params):
    return FlowInputs.from_scenario(params, "central")


@pytest.fixture(scope="session")
def central(central_inputs):
    return compute_flows(central_inputs)
