"""
Copyright [2009-2016] EMBL-European Bioinformatics Institute
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

import json

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from portal.models import Xref


class Importer():
    def load(self, filename):
        with open(filename, 'rb') as raw:
            return json.load(raw)

    def insert(self, data):
        coordinates = Xref.objects.\
            filter(upi=data['upi'], taxid=data['taxid']).\
            accession.\
            coordinates

        for coordinate in coordinates:
            coordinate.primary_start = data['primary_start']
            coordinate.primary_end = data['primary_end']
            coordinate.strand = data['strand']
            coordinate.chromosome = data['chromosome']
            coordinate.save()

    def __call__(self, json_file=None, **kwargs):
        data = self.load(json_file)
        for entry in data:
            self.insert(entry)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--input',
                    dest='json_file',
                    default=False,
                    help='[Required] Path to JSON mappings to import'),
    )
    help = (
        'Import computed genome coordinates to the database. This requires '
        'that the generic information about the sequence is already imported.'
    )

    def handle(self, *args, **kwargs):
        if not kwargs['json_file']:
            raise CommandError('Please specify input file')
        Importer()(**kwargs)
