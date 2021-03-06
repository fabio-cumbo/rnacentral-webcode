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

import json
import re

from django.db import models

from portal.config.genomes import get_ensembl_species_url


class Accession(models.Model):
    accession = models.CharField(max_length=100, primary_key=True)

    # in miRNAs mature products and precursor have the same parent_ac
    parent_ac = models.CharField(max_length=100)

    seq_version = models.IntegerField(db_index=True)
    feature_start = models.IntegerField(db_index=True)
    feature_end = models.IntegerField(db_index=True)

    # INSDC classification; 'ncRNA', unless it's rRNA/tRNA/precursor RNA
    feature_name = models.CharField(max_length=20)

    ordinal = models.IntegerField()
    division = models.CharField(max_length=3)
    keywords = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    species = models.CharField(max_length=150)
    organelle = models.CharField(max_length=100)
    classification = models.CharField(max_length=500)
    project = models.CharField(max_length=50)
    is_composite = models.CharField(max_length=1)
    non_coding_id = models.CharField(max_length=100)
    database = models.CharField(max_length=20)
    external_id = models.CharField(max_length=150)

    # GeneID (without coordinates); used to find splice variants for lncRNAs OR mature/precursor RNAs for miRNAs
    optional_id = models.CharField(max_length=100)
    common_name = models.CharField(max_length=200, default='')

    anticodon = models.CharField(max_length=50)
    experiment = models.CharField(max_length=500)
    function = models.CharField(max_length=500)
    gene = models.CharField(max_length=50)
    gene_synonym = models.CharField(max_length=400)
    inference = models.CharField(max_length=100)
    locus_tag = models.CharField(max_length=50)
    genome_position = models.CharField(max_length=200, db_column='map')
    mol_type = models.CharField(max_length=50)
    ncrna_class = models.CharField(max_length=50)
    note = models.CharField(max_length=1600)
    old_locus_tag = models.CharField(max_length=50)
    product = models.CharField(max_length=300)
    db_xref = models.CharField(max_length=800)
    standard_name = models.CharField(max_length=100, default='')

    class Meta:
        db_table = 'rnc_accessions'

    def get_pdb_entity_id(self):
        """Example PDB accession: 1J5E_A_1 (PDB id, chain, entity id)"""
        return self.accession.split('_')[-1] if self.database == 'PDBE' else None

    def get_pdb_structured_note(self):
        """
        Get 3D structure metadata stored in a structured note.
        * experimental technique
        * PDB structure title
        * release date
        """
        if self.database == "PDBE" and self.note:
            return json.loads(self.note)
        else:
            return None

    def get_hgnc_ensembl_id(self):
        """Extract Ensembl Gene id (if available) from the note json field."""
        if self.database == "HGNC" and self.note:
            note = json.loads(self.note)
            return note['ensembl_gene_id'] if 'ensembl_gene_id' in note else None
        else:
            return None

    def get_hgnc_id(self):
        """Search db_xref field for an HGNC id."""
        if self.db_xref:
            match = re.search(r'HGNC\:HGNC\:(\d+)', self.db_xref)
            return match.group(1) if match else None
        else:
            return None

    def get_biotype(self):
        """
        Biotype annotations are stored in notes and come from Ensembl and VEGA
        entries.
        Biotype is used to color entries in Genoverse.
        If biotype contains the word "RNA" it is given a predefined color.
        """
        biotype = 'ncRNA'  # default biotype
        if self.note:
            match = re.search(r'biotype\:(\w+)', self.note)
            if match:
                biotype = match.group(1)
        return biotype

    def get_rna_type(self):
        """
        Get the type of RNA, which either the name of the feature from the
        feature table in the Non-coding product, or for `ncRNA` features,
        it's one of the ncRNA classes defined by INSDC.
        """
        return self.ncrna_class if self.feature_name == 'ncRNA' else self.feature_name

    def get_srpdb_id(self):
        return re.sub('\.\d+$', '', self.external_id) if self.external_id else None

    def get_ena_url(self):
        """
        Get the ENA entry url that refers to the entry from
        the Non-coding product containing the cross-reference.
        """
        if self.database in ['RFAM', 'PDBE', 'REFSEQ', 'RDP', 'GtRNAdb', 'lncRNAdb', 'miRBase', 'pombase', 'Dictybase', 'SGD', 'snopy', 'Srpdb', 'tair', 'tmRNA website']:
            return ''  # no ENA source links for these entries
        ena_base_url = "http://www.ebi.ac.uk/ena/data/view/Non-coding:"
        if self.is_composite == 'Y':
            return ena_base_url + self.non_coding_id
        else:
            return ena_base_url + self.accession

    def get_ensembl_species_url(self):
        """Get species name in a format that can be used in Ensembl urls."""
        return get_ensembl_species_url(self.species, self.accession)

    def get_expert_db_external_url(self):
        """Get external url to expert database."""
        urls = {
            'RFAM': 'http://rfam.org/family/{id}',
            'SRPDB': 'http://rnp.uthscsa.edu/rnp/SRPDB/rna/sequences/fasta/{id}',
            'MIRBASE': 'http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc={id}',
            'TMRNA_WEB': 'http://bioinformatics.sandia.gov/tmrna/seqs/{id}',
            'LNCRNADB': 'http://www.lncrnadb.org/{id}',
            'REFSEQ': 'http://www.ncbi.nlm.nih.gov/nuccore/{id}.{version}',
            'RDP': 'http://rdp.cme.msu.edu/hierarchy/detail.jsp?seqid={id}',
            'SNOPY': 'http://snoopy.med.miyazaki-u.ac.jp/snorna_db.cgi?mode=sno_info&id={id}',
            'PDBE': 'http://www.ebi.ac.uk/pdbe-srv/view/entry/{id}',
            'SGD': 'http://www.yeastgenome.org/locus/{id}/overview',
            'TAIR': 'http://www.arabidopsis.org/servlets/TairObject?id={id}&type=locus',
            'WORMBASE': 'http://www.wormbase.org/species/c_elegans/gene/{id}',
            'PLNCDB': 'http://chualab.rockefeller.edu/cgi-bin/gb2/gbrowse_details/arabidopsis?name={id}',
            'DICTYBASE': 'http://dictybase.org/gene/{id}',
            'SILVA': 'http://www.arb-silva.de/browser/{lsu_ssu}/silva/{id}',
            'POMBASE': 'http://www.pombase.org/spombe/result/{id}',
            'GREENGENES': 'http://www.ebi.ac.uk/ena/data/view/{id}.{version}',
            'NONCODE': 'http://www.noncode.org/show_rna.php?id={id}&version={version}',
            'LNCIPEDIA': 'http://www.lncipedia.org/db/transcript/{id}',
            'MODOMICS': 'http://modomics.genesilico.pl/sequences/list/{id}',
            'HGNC': 'http://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id={id}',
            'ENSEMBL': 'http://www.ensembl.org/{species}/Transcript/Summary?t={id}',
            'GENCODE': 'http://www.ensembl.org/{species}/Transcript/Summary?t={id}',
            'FLYBASE': 'http://flybase.org/reports/{id}.html',
            'MGI': 'http://www.informatics.jax.org/marker/{id}',
            'GTRNADB': '',
            'RGD': 'https://rgd.mcw.edu/rgdweb/report/gene/main.html?id={id}'
        }
        if self.database in urls.keys():
            if self.database == 'GTRNADB':
                data = json.loads(self.note)
                if 'url' in data:
                    return data['url']
                else:
                    return ''
            elif self.database == 'LNCRNADB':
                return urls[self.database].format(id=self.optional_id.replace(' ', ''))
            elif self.database == 'VEGA':
                return urls[self.database].format(id=self.optional_id,
                    species=self.species.replace(' ', '_'))
            elif self.database == 'SILVA':
                return urls[self.database].format(id=self.optional_id,
                    lsu_ssu='ssu' if 'small' in self.product else 'lsu')
            elif self.database == 'GREENGENES':
                return urls[self.database].format(id=self.parent_ac, version=self.seq_version)
            elif self.database == 'REFSEQ':
                return urls[self.database].format(id=self.external_id, version=self.seq_version)
            elif self.database == 'NONCODE':
                noncode_id, version = self.external_id.split('.')
                return urls[self.database].format(id=noncode_id, version=version)
            elif self.database == 'HGNC':
                return urls[self.database].format(id=self.accession)
            elif self.database == 'ENSEMBL' or self.database == 'GENCODE':
                return urls[self.database].format(id=self.external_id, species=self.get_ensembl_species_url())
            return urls[self.database].format(id=self.external_id)
        else:
            return ''
