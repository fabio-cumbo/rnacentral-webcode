# -*- coding: utf-8 -*-

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

import os
from glob import glob
from pprint import pformat
import random

import requests

from django.db.models import Q
from django.core.management.base import BaseCommand

from portal.config.genomes import genomes
from portal.models import Accession

GENOMES_DIRECTORY = 'portal/static/node_modules/angularjs-genoverse/lib/Genoverse/js/genomes/'


class Command(BaseCommand):
    help = 'Get and pretty print all ensembl genome information'

    def fetch_ensembl_summary(self, url):
        response = requests.get(url, headers={
            "Content-Type": "application/json"
        })
        response.raise_for_status()
        data = response.json()
        mapping = {}
        for entry in data['species']:
            if entry['strain_collection']:
                continue
            name = entry['name'].replace('_', ' ')
            name = str(name[0].upper() + name[1:])
            synonyms = [str(a) for a in entry['aliases']]
            synonyms.append(str(entry['common_name']))
            taxid = int(entry['taxon_id'])

            mapping[taxid] = {
                'species': name,
                'synonyms': synonyms,
                'assembly': str(entry['assembly']),
                'assembly_ucsc': str(entry['assembly']),
                'taxid': taxid,
                'division': str(entry['division']),
            }
        return mapping

    def ensembl_genomes(self):
        url = "http://rest.ensembl.org/info/species?"
        return self.fetch_ensembl_summary(url)

    def genoverse_genomes(self):
        names = set()
        for filename in glob(os.path.join(GENOMES_DIRECTORY, '*.js')):
            # So we have to check if there is actually information in these
            # javascript files (why can't they be nice JSON to parse??) so we
            # check the number of lines. The empty ones have 1 line.
            with open(filename, 'rb') as raw:
                if len(raw.readlines()) <= 1:
                    continue
            name = os.path.basename(filename)
            name = name[:-3]
            names.add(name)
        return names

    def select_example(self, genome):
        print('Getting example for %s' % genome['species'])
        accessions = Accession.objects.filter(
            database='ENSEMBL',
            species=genome['species'],
            coordinates__accession__isnull=False
        )

        # Try to exclude things that look like they come from a 'bad'
        # chromosome. This means anything that may be a contig or some sort of
        # generic accession.
        found = accessions.exclude(
            Q(chromosome__contains='.') |
            Q(chromosome__contains='_') |
            Q(chromosome__contains=':') |
            Q(chromosome__icontains='scaffold') |
            Q(chromosome__icontains='ultra') |
            Q(chromosome__icontains='contig')
        )
        if not found.count():
            print('  May fetch gross chromosome')
            found = accessions

        if not found.count():
            print("NO coordinates for %s" % str(genome))
            return {'chromosome': '', 'start': 0, 'end': 0}

        accession = random.choice(found)
        print('Found %s' % accession.accession)
        return {
            'chromosome': str(accession.chromosome),
            'start': int(accession.feature_start),
            'end': int(accession.feature_end),
        }

    def handle(self, *args, **kwargs):
        known = self.ensembl_genomes()
        for genome in genomes:
            key = genome['taxid']
            if key in known:
                del known[key]

        genoverse = self.genoverse_genomes()
        for extra in known.values():
            geno_key = extra['species'].lower().replace(' ', '_')
            if geno_key not in genoverse:
                print("Skipping non-genoverse genome: %s" % extra)
                continue
            extra['example_location'] = self.select_example(extra)
            genomes.append(extra)

        # Now you might be asking to yourself, why did he turn a string into a
        # string? Well it turns out that data structure is written, not JSON
        # encoded, as a javascript data structure. This is very annoying
        # because python's unicode strings `u''` don't translate literally to
        # javascript. Nor do python's longs `1L`. Both of we which we get back
        # from the API/database. Thus all the casting above to make sure
        # everything can be read by javascript.
        content = pformat(genomes)
        with open('portal/config/genomes.py', 'w') as out:
            # Write ebi header
            out.write(__doc__)
            out.write('\n')
            out.write('genomes = %s\n' % content)
