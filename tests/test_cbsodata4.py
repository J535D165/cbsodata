import os
import shutil

import requests

import cbsodata4 as cbsodata
# testing deps
import pytest


datasets = [
    '82245NED'
]


TEST_ENV = 'test_env'


def setup_module(module):
    print('\nsetup_module()')

    if not os.path.exists(TEST_ENV):
        os.makedirs(TEST_ENV)


def teardown_module(module):
    print('teardown_module()')

    shutil.rmtree(TEST_ENV)


@pytest.mark.parametrize("dataset_id", datasets)
def test_observations(dataset_id):

    x = cbsodata.get_observations(dataset_id)

    assert len(x) > 100


@pytest.mark.parametrize("dataset_id", datasets)
def test_metadata(dataset_id):

    x = cbsodata.get_metadata(dataset_id)

    assert "MeasurementGroups" in x.keys()


@pytest.mark.parametrize("dataset_id", datasets)
def test_dataset_info(dataset_id):

    # testing
    info = cbsodata.get_dataset_info(dataset_id)

    assert isinstance(info, dict)


@pytest.mark.parametrize("dataset_id", datasets)
def test_catalog_info(dataset_id):

    # testing
    info = cbsodata.get_catalog_info(dataset_id)

    assert isinstance(info, dict)


@pytest.mark.parametrize("dataset_id", datasets)
def test_filter(dataset_id):

    x = cbsodata.get_dataset(dataset_id, filter="Id ge 1 and Id lt 10")

    assert len(x) == 9


@pytest.mark.parametrize("dataset_id", datasets)
def test_top_skip(dataset_id):

    x = cbsodata.get_dataset(dataset_id, top=10, skip=5)

    assert len(x) == 10
    assert x[0]["Id"] == 5
