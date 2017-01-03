# Copyright (c) 2016 Jonathan de Bruin

#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation
#  files (the "Software"), to deal in the Software without
#  restriction, including without limitation the rights to use,
#  copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following
#  conditions:

#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.

#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.

"""Statistics Netherlands opendata API client for Python"""

import os
import json

import requests


__version__ = "0.1.2"

CBSOPENDATA = "http://opendata.cbs.nl"
API = "ODataApi/odata"
BULK = "ODataFeed/odata"

CATALOG = "ODataCatalog"
FORMAT = "json"


def _get_table_url(table_id):
    """ Create a table url for the given table indentifier."""

    # http://opendata.cbs.nl/ODataApi/OData/37506wwm
    return "%(baseurl)s/%(bulk)s/%(table_id)s/" % \
        {"baseurl": CBSOPENDATA, "bulk": BULK, "table_id": table_id}


def _download_metadata(table_id, metadata_name, select=None, filters=None):
    """ Download metadata. """

    # http://opendata.cbs.nl/ODataApi/OData/37506wwm/UntypedDataSet?$format=json
    url = _get_table_url(table_id) + metadata_name

    params = {}
    params["$format"] = FORMAT

    if select:
        params['$select'] = _select(select=select)
    if filters:
        params['$filter'] = _filters(filters)

    data = []

    while (url is not None):

        r = requests.get(url, params=params)

        res = r.json(encoding='utf-8')
        res_value = res['value']

        data.extend(res_value)

        try:
            url = res['odata.nextLink']
        except KeyError:
            url = None

    return data


def _save_data(data, dir, metadata_name):
    """ Save the data. """

    print ("Write metadata '%s'" % metadata_name)

    if not os.path.exists(dir):
        os.makedirs(dir)

    fp = os.path.join(dir, metadata_name + '.json')

    with open(fp, 'w') as output_file:
        json.dump(data, output_file, indent=2)


def _filters(query):
    """ Filter query """

    return query


def _select(select=None):
    """
    Select columns.

    :param select: The columns to return.
    :type select: str, list

    :returns: URL parameter
    :rtype: str
    """

    if isinstance(select, list):
        select = ','.join(select)

    return select


def download_data(table_id, dir=None, typed=False, select=None, filters=None):
    """
    Download the CBS data and metadata.

    :param table_id: The indentifier of the table.
    :param dir: Folder to save data to. If not given, data is not stored on
            disk.
    :param typed: Return a typed data table. Default False.
    :param select: Column label or list of column labels to return.
    :param filters: Return only rows that agree on the filter.
    :type table_id: str
    :type dir: str
    :type typed: bool
    :type select: list
    :type filters: str

    :returns: The requested data.
    :rtype: list
    """

    # Start downloading data
    print("Retrieving data from table '%s'" % table_id)

    # http://opendata.cbs.nl/ODataApi/OData/37506wwm?$format=json
    metadata_tables = _download_metadata(table_id, "")

    # The names of the tables with metadata
    metadata_table_names = [table['name'] for table in metadata_tables]

    # Download only the typed or untyped data
    typed_or_not_str = "TypedDataSet" if typed else "UntypedDataSet"
    metadata_table_names.remove(typed_or_not_str)

    data = {}

    for table_name in metadata_table_names:

        # download table
        if table_name in ["TypedDataSet", "UntypedDataSet"]:
            metadata = _download_metadata(table_id, table_name,
                                          select=select, filters=filters)
        else:
            metadata = _download_metadata(table_id, table_name)

        data[table_name] = metadata

        # save the data
        if dir:
            _save_data(metadata, dir, table_name)

    print("Done!")

    return data


def get_table_list(select=None, filters=None):
    """
    Get a list of available tables.

    :param select: Column label or list of column labels to return.
    :param filters: Return only rows that agree on the filter.
    :type select: list
    :type filters: str

    :returns: Information about the available tables (list of dictionaries)
    :rtype: list

    """

    # http://opendata.cbs.nl/ODataCatalog/Tables?$format=json&$filter=ShortTit
    # le%20eq%20%27Zeggenschap%20bedrijven;%20banen,%20grootte%27

    # http://opendata.cbs.nl/ODataCatalog/Tables?$format=json
    url = "%(baseurl)s/%(catalog)s/Tables?$format=json" % \
        {"baseurl": CBSOPENDATA, "catalog": CATALOG}

    params = {}
    if select:
        params['$select'] = _select(select=select)
    if filters:
        params['$filter'] = _filters(filters)

    r = requests.get(url, params=params)
    res = r.json()

    return res['value']


def get_info(table_id):
    """
    Get information about a table.

    :param table_id: The indentifier of the table.
    :type table_id: str

    :returns: Table information
    :rtype: dict
    """

    info_list = _download_metadata(table_id, "TableInfos")

    if len(info_list) > 0:
        return info_list[0]
    else:
        return None


def get_meta(table_id, name):
    """
    Get the metadata of a table.

    :param table_id: The indentifier of the table.
    :param name: The name of the metadata (for example DataProperties).
    :type table_id: str
    :type name: str

    :returns: list with metadata (dict type)
    :rtype: list
    """

    return _download_metadata(table_id, name)


def get_data(table_id, dir=None, typed=False, select=None, filters=None):
    """
    Get the CBS data table.

    :param table_id: The indentifier of the table.
    :param dir: Folder to save data to. If not given, data is not stored
            on disk.
    :param typed: Return a typed data table. Default False.
    :param select: Column label or list of column labels to return.
    :param filters: Return only rows that agree on the filter.
    :type table_id: str
    :type dir: str
    :type typed: bool
    :type select: list
    :type filters: str

    :returns: The requested data.
    :rtype: list
    """

    metadata = download_data(table_id, dir=dir, typed=typed,
                             select=select, filters=filters)

    if "TypedDataSet" in metadata.keys():
        data = metadata["TypedDataSet"]
    else:
        data = metadata["UntypedDataSet"]

    exclude = [
        "TableInfos", "TypedDataSet", "UntypedDataSet",
        "DataProperties", "CategoryGroups"
    ]

    norm_cols = list(set(metadata.keys()) - set(exclude))

    for norm_col in norm_cols:
        metadata[norm_col] = {r['Key']: r for r in metadata[norm_col]}

    for i in range(0, len(data)):

        for norm_col in norm_cols:

            try:
                v = data[i][norm_col]
                data[i][norm_col] = metadata[norm_col][v]['Title']
            except KeyError:
                pass

    return data
