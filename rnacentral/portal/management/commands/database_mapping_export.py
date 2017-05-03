"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import csv
import operator as op

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from portal.management.commands.common_exporters.oracle_connection import \
    OracleConnection


class SingleExporter(OracleConnection):
    """
    This class is the callable that will compute and save the export for a
    database.
    """

    def external(self, database):
        """
        A method which will generate a function that generates the external id
        we use for the given database.
        """

        if database.upper() == 'PDBE':
            getter = op.itemgetter('external_id', 'optional_id')

            def fn(accession):
                return "_".join(getter(accession))
            return fn
        return op.itemgetter('external_id')

    def run_query(self, database):
        sql = '''
        select distinct
            rna.upi,
            acc.external_id,
            acc.optional_id
        from rna, xref, rnc_accessions acc
        where
            rna.upi = xref.upi
            and acc.accession = xref.ac
            and xref.deleted = 'N'
            and acc.database = :name
        order by upi, external_id, optional_id
        '''
        self.get_cursor()
        self.cursor.execute(sql, name=database.upper())

    def data(self, database):
        """
        Fetch the data for the given database.

        Yields
        ------
        A dict of 'external' and 'upi' for the external id and the RNAcentral
        UPI respectively.
        """
        self.run_query(database)
        external_generator = self.external(database)
        last = None
        for raw in self.cursor:
            row = self.row_to_dict(raw)
            result = (external_generator(row), row['upi'])
            if result != last:
                last = result
                yield result

    def __call__(self, database, filename):
        """
        Run the export for the given database, writing to the given file.
        """
        data = self.data(database)
        with open(filename, 'wb') as out:
            writer = csv.writer(out, delimiter='\t', quoting=csv.QUOTE_NONE)
            writer.writerows(data)


class Command(BaseCommand):
    """
    The handler class for Django.
    """

    option_list = BaseCommand.option_list + (
        make_option('-f', '--filename',
                    dest='filename',
                    default=False,
                    help='[Required] Path to file to write mapping to'),
        make_option('-d', '--database',
                    dest='database',
                    default=False,
                    help='[Required] Name of database to export'),
    )
    help = ('Export a mapping from external ID to RNAcentral ID')

    def handle(self, *args, **options):
        if not options['database']:
            raise CommandError('Must specify database to use')
        if not options['filename']:
            raise CommandError('Must specify an output filename')

        database = options.pop('database')
        filename = options.pop('filename')
        SingleExporter()(database, filename)
