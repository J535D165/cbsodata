Statistics Netherlands opendata API client for Python
=====================================================

|pypi| |travis|

.. |pypi| image:: https://badge.fury.io/py/cbsodata.svg
    :target: https://badge.fury.io/py/cbsodata

.. |travis| image:: https://travis-ci.org/J535D165/cbsodata.svg?branch=master
    :target: https://travis-ci.org/J535D165/cbsodata

Retrieve data from the `open data interface of Statistics
Netherlands <http://www.cbs.nl/nl-NL/menu/cijfers/statline/open-data/default.htm>`__
with *Python*.

R user? Use `cbsodataR <https://cran.r-project.org/web/packages/cbsodataR/index.html>`__. 

Installation
------------

From PyPi

.. code:: sh

    pip install cbsodata

Usage
-----

Load the package with

.. code:: python

    >>> import cbsodata

Tables
~~~~~~

``cbsodata.get_table_list(subset=None)``

Statistics Netherlands (CBS) has a large amount of public available
datatables (more than 4000 at the moment of writing). Each table is
idenitified with a unique identifier (``Identifier``).

.. code:: python

    >>> tables = cbsodata.get_table_list()
    >>> print(tables[0])
    {'Catalog': 'CBS',
     'ColumnCount': 18,
     'DefaultPresentation': '_la=nl&_si=&_gu=&_ed=LandVanUiteindelijkeZeggenschapUCI&_td=Perioden&graphType=line',
     'DefaultSelection': "$filter=((LandVanUiteindelijkeZeggenschapUCI eq '11111') or (LandVanUiteindelijkeZeggenschapUCI eq '22222')) and (Bedrijfsgrootte eq '10000') and (substringof('JJ',Perioden))&$select=LandVanUiteindelijkeZeggenschapUCI, Bedrijfsgrootte, Perioden, FiscaalJaarloonPerBaan_15",
     'ExplanatoryText': '',
     'Frequency': 'Perjaar',
     'GraphTypes': 'Table,Bar,Line',
     'ID': 0,
     'Identifier': '82010NED',
     'Language': 'nl',
     'MetaDataModified': '2014-02-04T02:00:00',
     'Modified': '2014-02-04T02:00:00',
     'OutputStatus': 'Regulier',
     'Period': '2008 t/m 2011',
     'ReasonDelivery': 'Actualisering',
     'RecordCount': 32,
     'SearchPriority': '2',
     'ShortDescription': '\nDeze tabel bevat informatie over banen en lonen bij bedrijven in Nederland, uitgesplitst naar het land van uiteindelijke zeggenschap van die bedrijven. Hierbij wordt onderscheid gemaakt tussen bedrijven onder Nederlandse zeggenschap en bedrijven onder buitenlandse zeggenschap. In de tabel zijn alleen de bedrijven met werknemers in loondienst meegenomen. De cijfers hebben betrekking op het totale aantal banen bij deze bedrijven en de samenstelling van die banen naar kenmerken van de werknemers (baanstatus, geslacht, leeftijd, herkomst en hoogte van het loon). Ook het gemiddelde fiscale jaarloon per baan is in de tabel te vinden. \n\nGegevens beschikbaar vanaf: 2008 \n\nStatus van de cijfers: \nDe cijfers in deze tabel zijn definitief.\n\nWijzigingen per 4 februari 2014\nDe cijfers van 2011 zijn toegevoegd.\n\nWanneer komen er nieuwe cijfers?\nDe cijfers over 2012 verschijnen in de eerste helft van 2015.\n',
     'ShortTitle': 'Zeggenschap bedrijven; banen, grootte',
     'Source': 'CBS.',
     'Summary': 'Banen en lonen van werknemers bij bedrijven in Nederland\nnaar land van uiteindelijke zeggenschap en bedrijfsgrootte',
     'SummaryAndLinks': 'Banen en lonen van werknemers bij bedrijven in Nederland<br />naar land van uiteindelijke zeggenschap en bedrijfsgrootte<br /><a href="http://opendata.cbs.nl/ODataApi/OData/82010NED">http://opendata.cbs.nl/ODataApi/OData/82010NED</a><br /><a href="http://opendata.cbs.nl/ODataFeed/OData/82010NED">http://opendata.cbs.nl/ODataFeed/OData/82010NED</a>',
     'Title': 'Zeggenschap bedrijven in Nederland; banen en lonen, bedrijfsgrootte',
     'Updated': '2014-02-04T02:00:00'}

Info
~~~~

``cbsodata.get_info(table_id)``

Get information about a table with the ``get_info`` function.

.. code:: python

    >>> info = cbsodata.get_info('82070ENG') # Returns a dict with info
    >>> info['Title']
    'Caribbean Netherlands; employed labour force characteristics 2012'
    >>> info['Modified']
    '2013-11-28T15:00:00'

Data
~~~~

``cbsodata.get_data(table_id, dir=None, typed=False)``

The function you are looking for!! The data is returned as a list of
dicts.

.. code:: python

    >>> data = cbsodata.get_data('82070ENG')
    [{'CaribbeanNetherlands': 'Bonaire',
      'EmployedLabourForceInternatDef_1': 8837,
      'EmployedLabourForceNationalDef_2': 8559,
      'Gender': 'Total male and female',
      'ID': 0,
      'Periods': '2012',
      'PersonalCharacteristics': 'Total personal characteristics'},
     {'CaribbeanNetherlands': 'St. Eustatius',
      'EmployedLabourForceInternatDef_1': 2099,
      'EmployedLabourForceNationalDef_2': 1940,
      'Gender': 'Total male and female',
      'ID': 1,
      'Periods': '2012',
      'PersonalCharacteristics': 'Total personal characteristics'},
     {'CaribbeanNetherlands': 'Saba',
      'EmployedLabourForceInternatDef_1': 1045,
      'EmployedLabourForceNationalDef_2': 971,
      'Gender': 'Total male and female',
      'ID': 2,
      'Periods': '2012',
      'PersonalCharacteristics': 'Total personal characteristics'},
     # ...
    ]

Pandas users
~~~~~~~~~~~~

The result can be converted in a pandas DataFrame.

.. code:: python

    >>> data = pandas.DataFrame(cbsodata.get_data('82070ENG'))
    >>> data.head()

The list of tables can be converted into a pandas DataFrame easily.

.. code:: python

    >>> tables = pandas.DataFrame(cbsodata.get_table_list())
    >>> tables.head()
