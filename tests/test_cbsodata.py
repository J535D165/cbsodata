import unittest
from nose_parameterized import parameterized

import os
import shutil

import cbsodata

datasets = [
    # '81252NED',
    # '82010NED',
    '80884ENG'
]

TEST_ENV = 'test_env'


class TestCBSOData(unittest.TestCase):

    @classmethod
    def setupClass(self):

        if not os.path.exists(TEST_ENV):
            os.makedirs(TEST_ENV)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(TEST_ENV)

    @parameterized.expand(datasets)
    def test_info(self, table_id):

        # testing
        info = cbsodata.get_info(table_id)

        self.assertIsInstance(info, dict)

    @parameterized.expand(datasets)
    def test_download(self, table_id):

        cbsodata.download_data(table_id)

    @parameterized.expand(datasets)
    def test_download_and_store(self, table_id):

        cbsodata.download_data(
            table_id,
            dir=os.path.join(TEST_ENV, table_id)
        )

        self.assertTrue(
            os.path.exists(
                os.path.join(TEST_ENV, table_id, 'TableInfos.json')
            )
        )

    @parameterized.expand(datasets)
    def test_get_data(self, table_id):

        cbsodata.get_data(table_id)

    @parameterized.expand(datasets)
    def test_info_values(self, table_id):

        info = cbsodata.get_info(table_id)

        # Check response is dict (not a list)
        self.assertIsInstance(info, dict)

        # Check required keys are available
        self.assertTrue('Description' in info.keys())
        self.assertTrue('ID' in info.keys())
        self.assertTrue('Identifier' in info.keys())

    def test_table_list(self):

        self.assertGreaterEqual(len(cbsodata.get_table_list()), 100)

    def test_filters(self):

        default_sel_filt = cbsodata.get_info('82070ENG')['DefaultSelection']
        filters_and_selections = default_sel_filt.split("&")

        print (filters_and_selections[0])

        for fs in filters_and_selections:
            if fs.startswith('$filter='):
                filt = fs[8:]

        print (filt)

        cbsodata.get_data('82070ENG', filters=filt)
