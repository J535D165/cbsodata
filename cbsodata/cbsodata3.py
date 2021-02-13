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

__all__ = ['download_data', 'get_data', 'get_info', 'get_meta',
           'get_table_list', 'options', 'catalog']

import os
import json
import copy
import logging
import warnings
from contextlib import contextmanager

import requests
from requests import Session, Request


CBSOPENDATA = "opendata.cbs.nl"  # deprecate in next version
API = "ODataApi/odata"
BULK = "ODataFeed/odata"

CATALOG = "ODataCatalog"
FORMAT = "json"


class OptionsManager(object):
    """Class for option management"""

    def __init__(self):

        self.use_https = True
        self.api_version = "3"
        # Get default proxy settings from environment variables
        proxies = {
            "http": os.environ.get("http_proxy", None),
            "https": os.environ.get("https_proxy", None),
        }
        self.requests = {"proxies": proxies}  # proxies, cert, verify

        # Enable in next version
        # self.catalog_url = "opendata.cbs.nl"

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "catalog_url = {}, use_https = {}".format(
            self.catalog_url, self.use_https)

    def __getitem__(self, arg):
        return getattr(self, arg)

    def __setitem__(self, arg, value):
        setattr(self, arg, value)

    def _log_setting_change(self, setting_name, old_value, new_value):
        logging.info(
            "Setting '{}' changed from '{}' to '{}'.".format(
                setting_name, old_value, new_value)
        )

    def __setattr__(self, arg, value):
        try:
            old_value = copy.copy(getattr(self, arg))
        except Exception:
            old_value = "undefined"

        self._log_setting_change(arg, old_value, value)
        super(OptionsManager, self).__setattr__(arg, value)

    @property
    def catalog_url(self):
        return CBSOPENDATA

    @catalog_url.setter
    def catalog_url(self, url):
        global CBSOPENDATA
        CBSOPENDATA = url  # noqa

    @property
    def proxies(self):
        return self.requests.get('proxies', None)

    @proxies.setter
    def proxies(self, proxies):
        warnings.warn(
            "Deprecated, use options.requests['proxies'] instead",
            DeprecationWarning
        )
        self.requests['proxies'] = proxies


# User options
options = OptionsManager()


def _get_catalog_url(url):

    return options.catalog_url if url is None else url


def _get_table_url(table_id, catalog_url=None):
    """Create a table url for the given table identifier."""

    if catalog_url is None:
        _catalog_url = options.catalog_url
    else:
        _catalog_url = catalog_url

    components = {"http": "https://" if options.use_https else "http://",
                  "baseurl": _catalog_url,
                  "bulk": BULK,
                  "table_id": table_id}

    # http://opendata.cbs.nl/ODataApi/OData/37506wwm
    return "{http}{baseurl}/{bulk}/{table_id}/".format(**components)


def _download_metadata(table_id, metadata_name, select=None, filters=None,
                       catalog_url=None, **kwargs):
    """Download metadata."""

    # http://opendata.cbs.nl/ODataApi/OData/37506wwm/UntypedDataSet?$format=json
    url = _get_table_url(table_id, catalog_url=catalog_url) + metadata_name

    params = {}
    params["$format"] = FORMAT

    if select:
        params['$select'] = _select(select)
    if filters:
        params['$filter'] = _filters(filters)

    # additional parameters to requests
    request_kwargs = options.requests.copy()
    request_kwargs.update(kwargs)

    try:
        data = []

        while (url is not None):

            s = Session()
            p = Request('GET', url, params=params).prepare()

            logging.info("Download " + p.url)

            r = s.send(p, **request_kwargs)
            r.raise_for_status()
            r.encoding = "utf-8"

            res = json.loads(r.text)
            data.extend(res['value'])

            try:
                url = res['odata.nextLink']
                params = {}
            except KeyError:
                url = None

        return data

    except requests.HTTPError as http_err:
        raise requests.HTTPError(
            "Downloading table '{}' failed. {}".format(table_id, str(http_err))
        )


def _save_data(data, dir, metadata_name):
    """Save the data."""

    if not os.path.exists(dir):
        os.makedirs(dir)

    fp = os.path.join(dir, metadata_name + '.json')

    with open(fp, 'w') as output_file:
        json.dump(data, output_file, indent=2)


def _filters(query):
    """Filter rows with a CBS-style query.

    Parameters
    ----------
    query : str
        The rows to return.

    Returns
    -------
    str
        Filter parameter for URL
    """

    return query


def _select(select):
    """Select columns.

    Parameters
    ----------
    select : str
        The columns to return.

    Returns
    -------
    str
        Select parameter for URL
    """

    if isinstance(select, list):
        select = ','.join(select)

    return select


def download_data(table_id, dir=None, typed=False, select=None, filters=None,
                  catalog_url=None, **kwargs):
    """Download the CBS data and metadata.

    Parameters
    ----------
    table_id : str
        The identifier of the table.
    dir : str
        Folder to save data to. If not given, data is not stored on
        disk.
    typed : bool
        Return a typed data table. Default False.
    select : str, list
        Column label or list of column labels to return.
    filters : str
        Return only rows that agree on the filter.
    catalog_url : str
        The url of the catalog. Default "opendata.cbs.nl".
    **kwargs :
        Optional arguments that ``requests.get()`` takes. For example,
        `proxies`, `cert` and `verify`.

    Returns
    -------
    list
        A dictionary with the (meta)data of the table
    """

    _catalog_url = _get_catalog_url(catalog_url)

    # http://opendata.cbs.nl/ODataApi/OData/37506wwm?$format=json
    metadata_tables = _download_metadata(
        table_id, "", catalog_url=_catalog_url, **kwargs
    )

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
                                          select=select, filters=filters,
                                          catalog_url=_catalog_url,
                                          **kwargs)
        else:
            metadata = _download_metadata(table_id, table_name,
                                          catalog_url=_catalog_url,
                                          **kwargs)

        data[table_name] = metadata

        # save the data
        if dir:
            _save_data(metadata, dir, table_name)

    return data


def get_table_list(select=None, filters=None, catalog_url=None, **kwargs):
    """Get a list with the available tables.

    Parameters
    ----------
    select : list, str
        Column label or list of column labels to return.
    filters : str
        Return only rows that agree on the filter.
    catalog_url : str
        The url of the catalog. Default "opendata.cbs.nl".
    **kwargs :
        Optional arguments that ``requests.get()`` takes. For example,
        `proxies`, `cert` and `verify`.

    Returns
    -------
    list
        A list with the description of each table in the catalog.
    """

    # http://opendata.cbs.nl/ODataCatalog/Tables?$format=json&$filter=ShortTit
    # le%20eq%20%27Zeggenschap%20bedrijven;%20banen,%20grootte%27

    # http://opendata.cbs.nl/ODataCatalog/Tables?$format=json

    _catalog_url = _get_catalog_url(catalog_url)

    components = {"http": "https://" if options.use_https else "http://",
                  "baseurl": _catalog_url,
                  "catalog": CATALOG}

    url = "{http}{baseurl}/{catalog}/Tables?$format=json".format(**components)

    params = {}
    if select:
        params['$select'] = _select(select)
    if filters:
        params['$filter'] = _filters(filters)

    # additional parameters to requests
    request_kwargs = options.requests.copy()
    request_kwargs.update(kwargs)

    try:
        s = Session()
        p = Request('GET', url, params=params).prepare()

        logging.info("Download " + p.url)

        r = s.send(p, **request_kwargs)
        r.raise_for_status()
        res = r.json()

        return res['value']

    except requests.HTTPError as http_err:
        raise requests.HTTPError(
            "Downloading table list failed. {}".format(str(http_err))
        )


def get_info(table_id, catalog_url=None, **kwargs):
    """Get information about a table.

    Parameters
    ----------
    table_id : str
        The identifier of the table.
    catalog_url : str
        The url of the catalog. Default "opendata.cbs.nl".
    **kwargs :
        Optional arguments that ``requests.get()`` takes. For example,
        `proxies`, `cert` and `verify`.

    Returns
    -------
    dict
        Table information
    """

    info_list = _download_metadata(
        table_id,
        "TableInfos",
        catalog_url=_get_catalog_url(catalog_url),
        **kwargs
    )

    if len(info_list) > 0:
        return info_list[0]
    else:
        return None


def get_meta(table_id, name, catalog_url=None, **kwargs):
    """Get the metadata of a table.

    Parameters
    ----------
    table_id : str
        The identifier of the table.
    name : str
        The name of the metadata (for example DataProperties).
    catalog_url : str
        The url of the catalog. Default "opendata.cbs.nl".
    **kwargs :
        Optional arguments that ``requests.get()`` takes. For example,
        `proxies`, `cert` and `verify`.

    Returns
    -------
    list
        A list with metadata (dict type)
    """

    return _download_metadata(
        table_id,
        name,
        catalog_url=_get_catalog_url(catalog_url),
        **kwargs
    )


def get_data(table_id, dir=None, typed=False, select=None, filters=None,
             catalog_url=None, **kwargs):
    """Get the CBS data table.

    Parameters
    ----------
    table_id : str
        The identifier of the table.
    dir : str
        Folder to save data to. If not given, data is not stored
            on disk.
    typed : bool
        Return a typed data table. Default False.
    select : list
        Column label or list of column labels to return.
    filters : str
        Return only rows that agree on the filter.
    catalog_url : str
        The url of the catalog. Default "opendata.cbs.nl".
    **kwargs :
        Optional arguments that ``requests.get()`` takes. For example,
        `proxies`, `cert` and `verify`.

    Returns
    -------
    list
        The requested data.
    """

    _catalog_url = _get_catalog_url(catalog_url)

    metadata = download_data(
        table_id,
        dir=dir,
        typed=typed,
        select=select,
        filters=filters,
        catalog_url=_catalog_url,
        **kwargs
    )

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


@contextmanager
def catalog(catalog_url, use_https=True):
    """Context manager for catalogs.

    Parameters
    ----------
    catalog_url : str
        Url for the catalog. For example:
        dataderden.cbs.nl.
    use_https : bool
        Use https. Default True.

    """

    old_url = copy.copy(options.catalog_url)
    options.catalog_url = catalog_url

    yield

    options.catalog_url = old_url
