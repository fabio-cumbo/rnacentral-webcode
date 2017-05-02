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

from portal.models import Xref

# from portal.management.commands.common_exporters.oracle_connection import \
#     OracleConnection


class SingleExporter(object):
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
            getter = op.attrgetter('external_id', 'optional_id')

            def fn(accession):
                return "_".join(getter(accession))
            return fn
        return op.attrgetter('external_id')

    def data(self, database):
        """
        Fetch the data for the given database.

        Yields
        ------
        A dict of 'external' and 'upi' for the external id and the RNAcentral
        UPI respectively.
        """
        query = Xref.objects.filter(deleted='N').\
            filter(db__descr=database.upper()).\
            select_related('accession', 'upi')

        external_generator = self.external(database)
        for row in query:
            yield (external_generator(row.accession), row.upi.upi)

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
