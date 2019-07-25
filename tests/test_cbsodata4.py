import os
import shutil

import cbsodata4 as cbsodata
# testing deps
import pytest


datasets = [
    '82245NED'
]

catalogs = [
    'CBS',
    'CBS-Maatwerk'
]

TEST_ENV = 'test_env'


def setup_module(module):
    print('\nsetup_module()')

    if not os.path.exists(TEST_ENV):
        os.makedirs(TEST_ENV)


def teardown_module(module):
    print('teardown_module()')

    shutil.rmtree(TEST_ENV)


def test_download():

    cbsodata.download_dataset(
        "81589NED",
        save_dir=os.path.join(TEST_ENV, "81589NED")
    )


@pytest.mark.parametrize("dataset_id", datasets)
def test_observations(dataset_id):

    x = cbsodata.get_observations(dataset_id)

    assert len(x) > 100


@pytest.mark.parametrize("dataset_id", datasets)
def test_metadata(dataset_id):

    x = cbsodata.get_metadata(dataset_id)

    assert "MeasureGroups" in x.keys()


@pytest.mark.parametrize("dataset_id", datasets)
def test_dataset_info(dataset_id):

    # testing
    info = cbsodata.get_dataset_info(dataset_id)

    assert isinstance(info, dict)


@pytest.mark.parametrize("catalog_id", catalogs)
def test_catalog_info(catalog_id):

    # testing
    info = cbsodata.get_catalog_info(catalog_id)

    assert isinstance(info, dict)


def test_catalog_info_error():

    with pytest.raises(ValueError):
        cbsodata.get_catalog_info("CBS-UNKNOWN")


@pytest.mark.parametrize("dataset_id", datasets)
def test_dataset_filter(dataset_id):

    x = cbsodata.get_dataset(dataset_id, filter="Id ge 1 and Id lt 10")

    assert len(x) == 9


@pytest.mark.parametrize("dataset_id", datasets)
def test_dataset_top_skip(dataset_id):

    x = cbsodata.get_dataset(dataset_id, top=10, skip=5)

    assert len(x) == 10
    assert x[0]["Id"] == 5


def test_dataset_measure_vars():

    dataset_id = '83487NED'

    # measure codes
    x = cbsodata.get_dataset(
        dataset_id,
        measure_vars=["Description"],
        top=10
    )

    assert "MeasureDescription" in x[0].keys()
    assert "MeasureTitle" not in x[0].keys()
    assert "Measure" in x[0].keys()

    x = cbsodata.get_dataset(
        dataset_id,
        include_measure_code_id=False,
        top=10
    )

    assert "Measure" not in x[0].keys()

    x = cbsodata.get_dataset(
        dataset_id,
        measure_group_vars=["Description"],
        include_measure_group_id=False,
        top=10
    )

    assert "MeasureGroupID" not in x[0].keys()
    assert "MeasureGroupDescription" in x[0].keys()
    assert "MeasureGroupTitle" not in x[0].keys()

    x = cbsodata.get_dataset(
        dataset_id,
        include_measure_group_id=True,
        top=10
    )

    assert "MeasureGroupID" in x[0].keys()


def test_dataset_drop_measure_id():

    x = cbsodata.get_data(
        "81589NED",
        measure_vars=None,
        measure_group_vars=None,
        include_measure_code_id=False,
        top=1
    )

    assert "Measure" not in x[0].keys()


def test_dataset_dimension_vars():

    dataset_id = '83487NED'

    # measure codes
    x = cbsodata.get_dataset(
        dataset_id,
        dimension_vars=["Description"],
        dimension_group_vars=[],
        top=10
    )

    assert "WijkenEnBuurtenDescription" in x[0].keys()
    assert "WijkenEnBuurtenTitle" not in x[0].keys()
    assert "WijkenEnBuurten" in x[0].keys()

    x = cbsodata.get_dataset(
        dataset_id,
        include_dimension_code_id=False,
        top=10
    )

    assert "WijkenEnBuurten" not in x[0].keys()

    x = cbsodata.get_dataset(
        dataset_id,
        dimension_group_vars=["Description"],
        include_dimension_group_id=False,
        top=10
    )

    assert "WijkenEnBuurtenGroupID" not in x[0].keys()
    assert "WijkenEnBuurtenGroupDescription" in x[0].keys()
    assert "WijkenEnBuurtenGroupTitle" not in x[0].keys()

    x = cbsodata.get_dataset(
        dataset_id,
        include_dimension_group_id=True,
        top=10
    )

    assert "WijkenEnBuurtenGroupID" in x[0].keys()


def test_dataset_drop_dimension_id():

    x = cbsodata.get_data(
        "81589NED",
        dimension_vars=None,
        dimension_group_vars=None,
        include_dimension_code_id=False,
        top=1
    )

    assert "Perioden" not in x[0].keys()
    assert "BedrijfstakkenBranchesSBI2008" not in x[0].keys()
