# Copyright (c) 2019 Jonathan de Bruin

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

try:
    from cbsodata._version import __version__
    from cbsodata._version import __version_tuple__
except ImportError:
    __version__ = "0.0.0"
    __version_tuple__ = (0, 0, 0)

from cbsodata.cbsodata3 import catalog
from cbsodata.cbsodata3 import download_data
from cbsodata.cbsodata3 import get_data
from cbsodata.cbsodata3 import get_info
from cbsodata.cbsodata3 import get_meta
from cbsodata.cbsodata3 import get_table_list
from cbsodata.cbsodata3 import options

__all__ = [
    "download_data",
    "get_data",
    "get_info",
    "get_meta",
    "get_table_list",
    "options",
    "catalog",
]
