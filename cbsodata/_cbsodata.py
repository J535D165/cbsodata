
import requests
import os
import json

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


def _download_metadata(table_id, metadata_name, params={}):
    """ Download metadata. """

    # http://opendata.cbs.nl/ODataApi/OData/37506wwm/UntypedDataSet?$format=json
    url = _get_table_url(table_id) + metadata_name

    params["$format"] = FORMAT

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


def _select(subset=None):
    """ Select columns. """

    params = {}

    if subset:
        if isinstance(subset, list):
            subset = ','.join(subset)

        params['$select'] = subset

    return params


def download_data(table_id, dir=None, typed=False):
    """
    Download the CBS data and metadata.

    :param table_id: The indentifier of the table.
    :param dir: Folder to save data to. If not given, data is not stored
            on disk.
    :param typed: Return a typed data table. Default False.
    :type table_id: str
    :type dir: str
    :type typed: bool

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
        metadata = _download_metadata(table_id, table_name)
        data[table_name] = metadata

        # save the data
        if dir:
            _save_data(metadata, dir, table_name)

    print("Done!")

    return data


def get_table_list(subset=None):
    """
    Get a list of available tables.

    :param subset: List of column label to return
    :type subset: list

    :returns: list of table infomation (dict type)
    :rtype: list

    """

    url = "%(baseurl)s/%(catalog)s/Tables?$format=json" % \
        {"baseurl": CBSOPENDATA, "catalog": CATALOG}

    params = _select(subset=subset)

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


def get_data(table_id, dir=None, typed=False):
    """
    Get the CBS table.

    :param table_id: The indentifier of the table.
    :param dir: Folder to save data to. If not given, data is not stored
            on disk.
    :param typed: Return a typed data table. Default False.
    :type table_id: str
    :type dir: str
    :type typed: bool

    :returns: The requested data.
    :rtype: list
    """

    metadata = download_data(table_id, dir=dir, typed=typed)

    if "TypedDataSet" in metadata.keys():
        data = metadata["TypedDataSet"]
    else:
        data = metadata["UntypedDataSet"]

    exclude = [
        "TableInfos", "TypedDataSet", "UntypedDataSet",
        "DataProperties", "CategoryGroups"
    ]

    # norm_cols = [meta for x in df.columns.tolist() if x in meta.keys()]
    norm_cols = set(metadata.keys()) - set(exclude)
    for norm_col in norm_cols:
        metadata[norm_col] = {r['Key']: r for r in metadata[norm_col]}

    for i in range(0, len(data)):

        for norm_col in norm_cols:

            v = data[i][norm_col]
            data[i][norm_col] = metadata[norm_col][v]['Title']

    return data
