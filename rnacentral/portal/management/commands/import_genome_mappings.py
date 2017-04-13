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

__doc__ = """
Import computed genome coordinates to the database. This requires that the
generic information about the sequence is already imported. In addition, this
version is very limited in that it cannot store data for things that have more
than one exon. However it will process all entries before attempting to save to
prevent partial updates.
"""


class Importer():
    def coordinate(self, data):
        xrefs = Xref.objects.\
            filter(upi=data['upi'], taxid=data['taxid'], deleted='N').\
            all()

        if not xrefs:
            print ValueError("No xrefs for %s found" % data)
            return None
        elif len(xrefs) > 1:
            print ValueError("Mulitple (%i) xrefs for %s found" % (len(xrefs), data))
            return None

        coordinates = xrefs.first().\
            accession.\
            coordinates.\
            all()

        if not coordinates:
            print("No existing coordinates found, cannot import %s" % data)
            return None
        elif len(coordinates) > 1:
            for coord in coordinates:
                print(coord.__dict__)
            print ValueError("Too many coordinates (%i) for %s" % (len(coordinates), data))
            return None

        coordinate = coordinates[0]
        if coordinate.primary_start is not None or \
                coordinate.primary_end is not None or \
                coordinate.chromosome:
            raise ValueError('Could not import because already existing data')
        return coordinate

    def update(self, data):
        if len(data['exons']) != 1:
            raise ValueError("Can only insert single exon mappings")

        coordinate = self.coordinate(data)
        if not coordinate:
            return None
        exon = data['exons'][0]
        coordinate.primary_start = exon['primary_start']
        coordinate.primary_end = exon['primary_end']
        coordinate.strand = exon['strand']
        coordinate.chromosome = exon['chromosome']
        return coordinate

    def __call__(self, filename, **kwargs):
        dry_run = kwargs.get('dry_run', False)
        with open(filename, 'rb') as raw:
            data = json.load(raw)

        # We process the entire dataset before saving to ensure we do end up in
        # a state where only some of the data has been inserted, which makes
        # debugging and rerunning harder.
        updated = (self.update(entry) for entry in data)
        updated = [u for u in updated if u]
        print("Found %i/%i insertable entries" % (len(updated), len(data)))

        if dry_run:
            print("Not saving because dry run")
        else:
            for coordinate in updated:
                coordinate.save()


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--input',
                    dest='json_file',
                    default=False,
                    help='[Required] Path to JSON mappings to import'),
        make_option('-d', '--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help='Dry run (do not save)')
    )

    help = __doc__

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        if not json_file:
            raise CommandError('Please specify input file')
        Importer()(json_file, **kwargs)
