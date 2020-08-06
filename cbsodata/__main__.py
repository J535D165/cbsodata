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

"""Statistics Netherlands opendata CLI client"""

import argparse
import json
import sys

import cbsodata

AVAILABLE_CMDS = ["data", "info", "list"]


def json_outputter(data_obj, max_rows=None):
    """Print data in JSON format."""

    # cut of the at max_rows
    if isinstance(max_rows, (int, float)):
        data_obj = data_obj[0:max_rows]

    for line in data_obj:
        print(json.dumps(line))


def text_outputter(data_obj, max_rows=None):
    """Print data in text format."""

    # cut of the at max_rows
    if isinstance(max_rows, (int, float)):
        data_obj = data_obj[0:max_rows]

    # collect the maximum length in each column
    value_max_len = {}
    for d in data_obj:
        for key, value in d.items():
            try:
                if len(str(value)) > value_max_len[key]:
                    value_max_len[key] = len(str(value))
            except KeyError:
                value_max_len[key] = len(str(value))

    # get a list of columns
    columns = value_max_len.keys()

    # check if the column name is larger than the largest value
    for col in columns:
        if len(str(col)) > value_max_len[col]:
            value_max_len[col] = len(str(col))

    # print the column line
    col_line = ""
    for i, col in enumerate(columns):
        if i != (len(columns) - 1):
            col_line = col_line + str(col) \
                .upper().ljust(value_max_len[col] + 2)
        else:
            col_line = col_line + str(col).upper()
    print(col_line)

    # print the data
    for d in data_obj:
        line = ""
        for i, col in enumerate(columns):
            if i != (len(columns) - 1):
                try:
                    line = line + str(d[col]).ljust(value_max_len[col] + 2)
                except KeyError:
                    line = " " * (value_max_len[col] + 2)
            else:
                try:
                    line = line + str(d[col])
                except KeyError:
                    pass
        print(line)


def parse_argument_table_id(parser):
    parser.add_argument(
        "table_id",
        type=str,
        help="table identifier"
    )


def parse_argument_catalog(parser):
    parser.add_argument(
        "--catalog_url",
        default=None,
        type=str,
        help="the catalog to download the data from")


def parse_argument_output_format(parser):
    parser.add_argument(
        "--output_format", "-f",
        default="json",
        type=str,
        help="format to show table ('json', 'text')")


def parse_argument_output(parser):
    parser.add_argument(
        "--output_file", "-o",
        default=None,
        type=str,
        help="file to store the output (only json support)")


def parse_argument_max_rows(parser):
    parser.add_argument(
        "--max_rows", "-n",
        default=100,
        type=int,
        help="maximum number of rows to output")


def save_list_to_json(data_obj, fp):
    """Write list with dicts to json"""

    with open(fp, 'w+') as f:
        for line in data_obj:
            f.write(json.dumps(line) + "\n")


def main():

    if len(sys.argv) > 1 and sys.argv[1] == "data":
        parser = argparse.ArgumentParser(
            prog="cbsodata",
            description="""
                CBS Open Data: Command Line Interface

                Get data by table identifier.
            """
        )
        parse_argument_table_id(parser)
        parse_argument_catalog(parser)
        parse_argument_output_format(parser)
        parse_argument_max_rows(parser)
        parse_argument_output(parser)
        args = parser.parse_args(sys.argv[2:])

        result = cbsodata.get_data(args.table_id, catalog_url=args.catalog_url)

        if args.output_file:
            save_list_to_json(result, args.output_file)

        if args.output_format == "text":
            text_outputter(result, max_rows=args.max_rows)
        else:
            json_outputter(result, max_rows=args.max_rows)

    elif len(sys.argv) > 1 and sys.argv[1] == "info":
        parser = argparse.ArgumentParser(
            prog="cbsodata",
            description="""
                CBS Open Data: Command Line Interface

                Get data infomation by table identifier.
            """
        )
        parse_argument_table_id(parser)
        parse_argument_catalog(parser)
        parse_argument_output_format(parser)
        parse_argument_output(parser)
        args = parser.parse_args(sys.argv[2:])

        result = cbsodata.get_info(args.table_id, catalog_url=args.catalog_url)

        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(result, f, indent=4)

        if args.output_format == "text":
            text_outputter(
                [{"Label": k, "Value": v} for k, v in result.items()]
            )
        else:
            print(json.dumps(result, indent=4))

    elif len(sys.argv) > 1 and sys.argv[1] == "list":
        parser = argparse.ArgumentParser(
            prog="cbsodata",
            description="""
                CBS Open Data: Command Line Interface

                Get list of available tables.
            """
        )
        parse_argument_catalog(parser)
        parse_argument_output_format(parser)
        parse_argument_max_rows(parser)
        parse_argument_output(parser)
        args = parser.parse_args(sys.argv[2:])

        result = cbsodata.get_table_list(catalog_url=args.catalog_url)

        if args.output_file:
            save_list_to_json(result, args.output_file)

        if args.output_format == "text":
            text_outputter(result, max_rows=args.max_rows)
        else:
            json_outputter(result, max_rows=args.max_rows)

    # no valid sub command
    else:
        parser = argparse.ArgumentParser(
            prog="cbsodata",
            description="""
                CBS Open Data: Command Line Interface
            """
        )
        parser.add_argument(
            "subcommand",
            nargs="?",
            type=lambda x: isinstance(x, str) and x in AVAILABLE_CMDS,
            help="the subcommand (one of '{}')".format(
                "', '".join(AVAILABLE_CMDS))
        )
        parser.add_argument(
            "--version",
            action='store_true',
            help="show the package version")

        args = parser.parse_args()

        if args.subcommand is None:
            parser.print_help()


if __name__ == '__main__':
    main()
