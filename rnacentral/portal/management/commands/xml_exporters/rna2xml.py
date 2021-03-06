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

import re
import json
from xml.sax import saxutils

import psycopg2

from ..common_exporters.database_connection import get_db_connection


INSDC_PATTERN = r'Submitted \(\d{2}\-\w{3}\-\d{4}\) to the INSDC\. ?'


def format_whitespace(text):
    """
    Strip out useless whitespace.
    """

    # delete empty lines (if gene_synonym is empty e.g. )
    text = re.sub(r'\n\s+\n', '\n', text)
    # delete whitespace at the beginning of lines
    return re.sub('\n +', '\n', text)


def preprocess_data(field, value):
    """
    Final data clean up and reformatting.
    """

    if field == 'gene_synonym':
        return value.replace(' ', ';')  # EBI search team request
    return value


def wrap_in_field_tag(name, value):
    """
    A method for creating field tags.
    """

    try:
        result = '<field name="{0}">{1}</field>'.format(name, value)
    except UnicodeEncodeError:
        value = value.encode('ascii', 'ignore').decode('ascii')
        result = '<field name="{0}">{1}</field>'.format(name, value)
    return result


def store_rfam_data(data, result):
    """
    Modify data to contain the Rfam annotation information.
    """

    data['rfam_family_name'].add(result['rfam_family_name'])
    data['rfam_id'].add(result['rfam_id'])
    data['rfam_clan'].add(result['rfam_clan'])

    status = {'problems': [], 'has_issue': False}
    if result['rfam_status']:
        status = json.loads(result['rfam_status'])

    for problem in status['problems']:
        data['rfam_problems'].add(problem['name'])


def store_computed_data(data, result):
    """
    This will store some computed values for gene if possible.
    """

    product_pattern = re.compile(r'^\w{3}-')
    if not result['gene'] and \
            result['product'] and \
            re.match(product_pattern, result['product']) and \
            result['expert_db'] == 'miRBase':
        short_gene = re.sub(product_pattern, '', result['product'])
        data['gene'].add(saxutils.escape(short_gene))


def store_redundant_fields(data, result, redundant_fields):
    """
    Store redundant data in sets in order to get distinct values.
    Escape '&', '<', and '>'.
    """

    escape_fields = [
        'species',
        'product',
        'common_name',
        'function',
        'gene',
        'gene_synonym',
    ]
    for field in redundant_fields:
        if result[field]:
            if field in escape_fields:
                result[field] = saxutils.escape(result[field])
            data[field].add(result[field])


def store_xrefs(data, result):
    """
    Store xrefs as (database, accession) tuples in self.data['xrefs'].
    """

    # skip PDB and SILVA optional_ids because for PDB it's chain id
    # and for SILVA it's INSDC accessions
    if result['expert_db'] not in ['SILVA', 'PDB'] and result['optional_id']:
        data['xrefs'].add((result['expert_db'], result['optional_id']))

    # expert_db should not contain spaces, EBeye requirement
    result['expert_db'] = result['expert_db'].replace(' ', '_').upper()

    # an expert_db entry
    if result['non_coding_id'] or result['expert_db']:
        data['xrefs'].add((result['expert_db'], result['external_id']))
    else:  # source ENA entry
        # Non-coding entry
        expert_db = 'NON-CODING'  # EBeye requirement
        data['xrefs'].add((expert_db, result['accession']))

    # parent ENA entry
    # except for PDB entries which are not based on ENA accessions
    if result['expert_db'] != 'PDBE':
        data['xrefs'].add(('ENA', result['parent_accession']))

    # HGNC entry: store a special flag and index accession
    if result['expert_db'] == 'HGNC':
        data['hgnc'] = True
        data['xrefs'].add(('HGNC', result['accession']))

    if result['note']:
        # extract GO terms from `note`
        for go_term in re.findall(r'GO\:\d+', result['note']):
            data['xrefs'].add(('GO', go_term))

        # extract SO terms from `note`
        for so_term in re.findall(r'SO\:\d+', result['note']):
            data['xrefs'].add(('SO', so_term))

        # extract ECO terms from `note`
        for eco_term in re.findall(r'ECO\:\d+', result['note']):
            data['xrefs'].add(('ECO', eco_term))


def get_rna_type(result):
    """
    Use either feature name or ncRNA class (when feature is 'ncRNA')
    """

    rna_type = None
    if result['rna_type']:
        rna_type = result['rna_type']
    else:
        if result['ncrna_class']:
            rna_type = result['ncrna_class']
        else:
            rna_type = result['feature_name']
    return [rna_type.replace('_', ' ')]


class RnaXmlExporter(object):
    """
    A class for outputting data about unique RNA sequences in xml dump format
    used for metadata indexing.
    The same class instance is reused for multiple URS to avoid recreating
    class instances and reuse database connection.
    """

    def __init__(self):
        """
        Connect to the database and set up all variables.
        """

        self.sql_statement = """
        SELECT t1.taxid, t1.deleted,
               t2.species, t2.organelle, t2.external_id, t2.optional_id,
               t2.non_coding_id, t2.accession,
               t2.function, t2.gene, t2.gene_synonym, t2.feature_name,
               t2.ncrna_class, t2.product, t2.common_name, t2.note,
               t2.parent_ac || '.' || t2.seq_version as parent_accession,
               t3.display_name as expert_db,
               t4.timestamp as created,
               t5.timestamp as last,
               t6.len as length,
               t7.rna_type,
               t2.locus_tag,
               t2.standard_name,
               t2.classification as tax_string,
               models.short_name as rfam_family_name,
               models.rfam_model_id as rfam_id,
               clans.rfam_clan_id as rfam_clan,
               t7.rfam_problems as rfam_status
        FROM xref t1
        JOIN rnc_accessions t2 ON t1.ac = t2.accession
        JOIN rnc_database t3 ON t1.dbid = t3.id
        JOIN rnc_release t4 on t1.created = t4.id
        JOIN rnc_release t5 on t1.last = t5.id
        JOIN rna t6 on t1.upi = t6.upi
        JOIN rnc_rna_precomputed t7 on t1.upi = t7.upi and t1.taxid = t7.taxid
        LEFT JOIN rfam_model_hits hits ON t1.upi = hits.upi
        LEFT JOIN rfam_models models
        ON hits.rfam_model_id = models.rfam_model_id
        LEFT JOIN rfam_clans clans ON models.rfam_clan_id = clans.rfam_clan_id
        WHERE
            t1.upi = '{upi}' AND
            t1.deleted = 'N' AND
            t1.taxid = {taxid}
        """

        self.data = dict()

        # fields with redundant values; for example, a single sequence
        # can be associated with multiple taxids.
        # these strings must match the SQL query return values
        # and will become keys in self.data
        self.redundant_fields = [
            'taxid', 'species', 'expert_db', 'organelle',
            'created', 'last', 'deleted',
            'function', 'gene', 'gene_synonym', 'note',
            'product', 'common_name', 'parent_accession',
            'optional_id', 'locus_tag', 'standard_name',
            'rfam_family_name', 'rfam_id', 'rfam_clan'
        ]

        # other data fields for which the sets should be (re-)created
        self.data_fields = [
            'rna_type', 'authors', 'journal', 'popular_species',
            'pub_title', 'pub_id', 'insdc_submission', 'xrefs',
            'rfam_problem_found', 'rfam_problems', 'tax_string'
        ]

        self.popular_species = set([
            9606,    # human
            10090,   # mouse
            7955,    # zebrafish
            3702,    # Arabidopsis thaliana
            6239,    # Caenorhabditis elegans
            7227,    # Drosophila melanogaster
            559292,  # Saccharomyces cerevisiae S288c
            4896,    # Schizosaccharomyces pombe
            511145,  # Escherichia coli str. K-12 substr. MG1655
            224308,  # Bacillus subtilis subsp. subtilis str. 168
        ])

        self.reset()
        conn = get_db_connection()
        self.cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def reset(self):
        """
        Initialize or reset self.data so that the same object can be reused
        for different sequences.
        """
        self.data = {
            'upi': None,
            'md5': None,
            'boost': None,
            'length': 0,
            'description_line': None,
        }

        # (re-)create sets for all data fields
        for field in self.redundant_fields + self.data_fields:
            self.data[field] = set()

    def retrieve_data_from_database(self, upi, taxid):
        """
        Some data is retrieved directly from the database because
        django ORM creates too much overhead.
        """

        self.cursor.execute(self.sql_statement.format(upi=upi, taxid=taxid))
        for result in self.cursor:
            store_redundant_fields(self.data, result, self.redundant_fields)
            store_xrefs(self.data, result)
            store_computed_data(self.data, result)
            store_rfam_data(self.data, result)
            self.data['rna_type'].update(get_rna_type(result))
            self.data['tax_string'].add(saxutils.escape(result['tax_string']))

        self.data['rfam_problem_found'] = [str(bool(self.data['rfam_problems']))]
        if not self.data['rfam_problems']:
            self.data['rfam_problems'].add('none')

    def is_active(self):
        """
        Return 'Active' if a sequence has at least one active cross_reference,
        return 'Obsolete' otherwise.
        """
        if 'N' in self.data['deleted']:
            return 'Active'
        else:
            return 'Obsolete'

    def __first_or_last_seen(self, mode):
        """
        Single method for retrieving first/last release dates.
        """
        if mode not in ['created', 'last']:
            return None
        self.data[mode] = list(self.data[mode])  # sets cannot be sorted
        self.data[mode].sort()
        if mode == 'created':
            value = self.data[mode][0]  # first
        elif mode == 'last':
            value = self.data[mode][-1]  # last
        return value.strftime('%d %b %Y')  # 18 Nov 2014 e.g.

    def first_seen(self):
        """
        Return the earliest release date.
        """
        return self.__first_or_last_seen('created')

    def last_seen(self):
        """
        Return the latest release date.
        """
        return self.__first_or_last_seen('last')

    def store_literature_references(self, rna, taxid):
        """
        Store literature reference data.
        """

        def process_location(location):
            """
            Store the location field either as journal or INSDC submission.
            """
            if re.match('^Submitted', location):
                location = re.sub(INSDC_PATTERN, '', location)
                if location:
                    self.data['insdc_submission'].add(location)
            else:
                if location:
                    self.data['journal'].add(location)

        for ref in rna.get_publications(taxid=taxid):
            self.data['pub_id'].add(ref.id)
            if ref.authors:
                self.data['authors'].add(ref.authors)
            if ref.title:
                self.data['pub_title'].add(saxutils.escape(ref.title))
            if ref.pubmed:
                self.data['xrefs'].add(('PUBMED', ref.pubmed))
            if ref.doi:
                self.data['xrefs'].add(('DOI', ref.doi))
            if ref.location:
                process_location(saxutils.escape(ref.location))

    def compute_boost_value(self):
        """
        Determine ordering in search results.
        """
        if self.is_active() == 'Active' and 'hgnc' in self.data:
            # highest priority for HGNC entries
            boost = 4
        elif self.is_active() == 'Active' and 9606 in self.data['taxid']:
            # human entries have max priority
            boost = 3
        elif self.is_active() == 'Active' and \
                self.popular_species & self.data['taxid']:
            # popular species are given priority
            boost = 2
        elif self.is_active() == 'Obsolete':
            # no priority for obsolete entries
            boost = 0
        else:
            # basic priority level
            boost = 1

        generic_types = set(['misc_RNA', 'misc RNA', 'other'])
        if len(self.data['rna_type']) == 1 and \
                generic_types.intersection(self.data['rna_type']):
            boost = boost - 0.5

        if 'incomplete_sequence' in self.data['rfam_problems']:
            boost = boost - 0.5

        self.data['boost'] = boost

    def format_field(self, field):
        """
        Wrap additional fields in <field name=""></field> tags.
        """
        text = []
        for value in self.data[field]:
            if value:  # organelle can be empty e.g.
                value = preprocess_data(field, value)
                text.append(wrap_in_field_tag(field, value))
        return '\n'.join(text)

    def format_cross_references(self, taxid):
        """
        Wrap xrefs and taxids in <ref dbname="" dbkey=""/> tags.
        Taxids are stored as cross-references.
        """

        text = []
        for xref in self.data['xrefs']:
            if not xref[1]:
                continue
            text.append('<ref dbname="{0}" dbkey="{1}" />'.format(
                xref[0],
                xref[1],
            ))

        for taxid in self.data['taxid']:
            text.append('<ref dbkey="{0}" dbname="ncbi_taxonomy_id" />'.format(
                taxid,
            ))

        return '\n'.join(text)

    def format_xml_entry(self, taxid):
        """
        Format self.data as an xml entry.
        Using Django templates is slower than constructing the entry manually.
        """

        def format_author_fields():
            """
            Store authors in separate tags to enable more precise searching.
            """
            authors = set()
            for author_list in self.data['authors']:
                for author in author_list.split(', '):
                    authors.add(author)
            return '\n'.join([wrap_in_field_tag('author', x) for x in authors])

        text = """
        <entry id="{upi}_{taxid}">
            <name>Unique RNA Sequence {upi}_{taxid}</name>
            <description>{description}</description>
            <dates>
                <date value="{first_seen}" type="first_seen" />
                <date value="{last_seen}" type="last_seen" />
            </dates>
            <cross_references>
                {cross_references}
            </cross_references>
            <additional_fields>
                {is_active}
                {length}
                {species}
                {organelles}
                {expert_dbs}
                {common_name}
                {function}
                {gene}
                {gene_synonym}
                {rna_type}
                {product}
                {has_genomic_coordinates}
                {md5}
                {authors}
                {journal}
                {insdc_submission}
                {pub_title}
                {pub_id}
                {popular_species}
                {boost}
                {locus_tag}
                {standard_name}
                {rfam_family_name}
                {rfam_id}
                {rfam_clan}
                {rfam_problem}
                {rfam_problem_found}
                {tax_string}
            </additional_fields>
        </entry>
        """.format(
            upi=self.data['upi'],
            description=self.data['description_line'],
            first_seen=self.first_seen(),
            last_seen=self.last_seen(),
            cross_references=self.format_cross_references(taxid),
            is_active=wrap_in_field_tag('active', self.is_active()),
            length=wrap_in_field_tag('length', self.data['length']),
            species=self.format_field('species'),
            organelles=self.format_field('organelle'),
            expert_dbs=self.format_field('expert_db'),
            common_name=self.format_field('common_name'),
            function=self.format_field('function'),
            gene=self.format_field('gene'),
            gene_synonym=self.format_field('gene_synonym'),
            rna_type=self.format_field('rna_type'),
            product=self.format_field('product'),
            has_genomic_coordinates=wrap_in_field_tag(
                'has_genomic_coordinates',
                str(self.data['has_genomic_coordinates'])
            ),
            md5=wrap_in_field_tag('md5', self.data['md5']),
            authors=format_author_fields(),
            journal=self.format_field('journal'),
            insdc_submission=self.format_field('insdc_submission'),
            pub_title=self.format_field('pub_title'),
            pub_id=self.format_field('pub_id'),
            popular_species=self.format_field('popular_species'),
            boost=wrap_in_field_tag('boost', self.data['boost']),
            locus_tag=self.format_field('locus_tag'),
            standard_name=self.format_field('standard_name'),
            taxid=taxid,
            rfam_family_name=self.format_field('rfam_family_name'),
            rfam_id=self.format_field('rfam_id'),
            rfam_clan=self.format_field('rfam_clan'),
            rfam_problem=self.format_field('rfam_problems'),
            rfam_problem_found=self.format_field('rfam_problem_found'),
            tax_string=self.format_field('tax_string'),
        )
        return format_whitespace(text)

    ##################
    # Public methods #
    ##################

    def get_xml_entry(self, rna):
        """
        Public method for outputting an xml dump entry for a given UPI.
        """
        taxids = rna.xrefs.values_list('taxid', flat=True).distinct()
        text = ''
        for taxid in taxids:
            self.reset()
            self.data['upi'] = rna.upi
            self.data['md5'] = rna.md5
            self.data['length'] = rna.length
            self.data['description_line'] = \
                saxutils.escape(rna.get_description(taxid=taxid))
            self.data['has_genomic_coordinates'] = \
                rna.has_genomic_coordinates(taxid=taxid)

            self.retrieve_data_from_database(rna.upi, taxid)
            if not self.data['xrefs']:
                continue

            self.store_literature_references(rna, taxid)
            self.data['popular_species'] = \
                self.data['taxid'] & self.popular_species

            self.compute_boost_value()
            text += self.format_xml_entry(taxid)
        return text
