"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

"""
Expert databases.
"""
expert_dbs = [
    {
        'name': 'ENA',
        'label': 'ena',
        'url': 'http://www.ebi.ac.uk/ena/',
        'description': "provides a comprehensive record of the world's nucleotide sequencing information",
        'abbreviation': 'European Nucleotide Archive',
        'examples': ['URS00002D0E0C', 'URS000035EE7E', 'URS0000000001'],
        'references': [
            {
                'title': 'Facing growth in the European Nucleotide Archive',
                'authors': 'Cochrane G, Alako B, Amid C, Bower L, Cerdeno-Tarraga A, Cleland I, Gibson R, Goodgame N, Jang M, Kay S et al.',
                'journal': 'Nucleic Acids Res. 2013 Jan;41(Database issue):D30-5',
                'pubmed_id': 23203883,
            },
            {
                'title': 'Assembly information services in the European Nucleotide Archive',
                'authors': 'Pakseresht N, Alako B, Amid C, Cerdeno-Tarraga A, Cleland I, Gibson R, Goodgame N, Gur T, Jang M, Kay S et al.',
                'journal': 'Nucleic Acids Res. 2014 Jan;42(Database issue):D38-43',
                'pubmed_id': 24214989,
            },
        ],
        'imported': True,
    },
    {
        'name': 'PDB',
        'label': 'pdb',
        'url': 'http://www.wwpdb.org/',
        'description': 'is the single worldwide repository of information about the 3D structures of large biological molecules',
        'abbreviation': 'Protein Data Bank',
        'examples': ['URS00007BBA28', 'URS00007BBC98', 'URS00007BBC5B'],
        'references': [
            {
                'title': 'Announcing the worldwide Protein Data Bank',
                'authors': 'Berman H, Henrick K, Nakamura H',
                'journal': 'Nat Struct Biol. 2003 Dec;10(12):980.',
                'pubmed_id': 14634627,
            },
        ],
        'imported': True,
    },
    {
        'name': 'FlyBase',
        'label': '',
        'url': 'http://flybase.org/',
        'description': 'a database of Dropsophila genes and genomes',
        'abbreviation': '',
        'examples': [],
        'references': [],
        'imported': False,
    },
    {
        'name': 'Rfam',
        'label': 'rfam',
        'url': 'http://rfam.xfam.org',
        'description': 'is a database containing information about ncRNA families and other structured RNA elements',
        'abbreviation': '',
        'examples': ['URS00000478B7', 'URS000066DAB6', 'URS000068EEC5'],
        'references': [
            {
                'title': 'Rfam 11.0: 10 years of RNA families',
                'authors': 'Burge SW, Daub J, Eberhardt R, Tate J, Barquist L, Nawrocki EP, Eddy SR, Gardner PP, Bateman A',
                'journal': 'Nucleic Acids Res. 2013 Jan;41(Database issue):D226-32',
                'pubmed_id': 23125362,
            },
        ],
        'imported': True,
    },
    {
        'name': 'miRBase',
        'label': 'mirbase',
        'url': 'http://www.mirbase.org/',
        'description': 'is a database of published miRNA sequences and annotations that provides a centralised system for assigning names to miRNA genes',
        'abbreviation': '',
        'examples': ['URS000075A685', 'URS00003B7674', 'URS000016FD1A'],
        'references': [
            {
                'title': 'miRBase: integrating microRNA annotation and deep-sequencing data',
                'authors': 'Kozomara A., Griffiths-Jones S.',
                'journal': 'Nucleic Acids Res. 39(Database issue): D152-7 (2011 Jan)',
                'pubmed_id': 21037258,
            },
        ],
        'imported': True,
    },
    {
        'name': 'Vega',
        'label': 'vega',
        'url': 'http://vega.sanger.ac.uk/',
        'description': """is a repository for high-quality gene models produced by the manual annotation of vertebrate genomes.
                          Human and mouse data from Vega are merged into <a href="http://www.gencodegenes.org/" target="_blank">GENCODE</a>""",
        'abbreviation': 'Vertebrate Genome Annotation',
        'examples': ['URS00000B15DA', 'URS00000A54A6', 'URS0000301B08'],
        'references': [
            {
                'title': 'The GENCODE v7 catalog of human long noncoding RNAs: analysis of their gene structure, evolution, and expression.',
                'authors': 'Derrien T., Johnson R., Bussotti G., Tanzer A., Djebali S., Tilgner H., Guernec G., Martin D., Merkel A., Knowles DG. et al.',
                'journal': 'Genome Res. 22(9): 1775-1789 (2012 Sep)',
                'pubmed_id': 22955988,
            },
            {
                'title': 'GENCODE: the reference human genome annotation for The ENCODE Project',
                'authors': 'Harrow J., Frankish A., Gonzalez JM., Tapanari E., Diekhans M., Kokocinski F., Aken BL., Barrell D., Zadissa A., Searle S. et al.',
                'journal': 'Genome Res. 22(9): 1760-1774 (2012 Sep)',
                'pubmed_id': 22955987,
            },
        ],
        'imported': True,
    },
    {
        'name': 'tmRNA Website',
        'label': 'tmrna-website',
        'url': 'http://bioinformatics.sandia.gov/tmrna/',
        'description': 'contains predicted tmRNA sequences from RefSeq prokaryotic genomes, plasmids and phages',
        'abbreviation': '',
        'examples': ['URS000060F5B3', 'URS000058C344', 'URS000048A91D'],
        'references': [
            {
                'title': 'The tmRNA website: reductive evolution of tmRNA in plastids and other endosymbionts',
                'authors': 'Gueneau de Novoa P., Williams KP.',
                'journal': 'Nucleic Acids Res. 32(Database issue): D104-8 (2004 Jan)',
                'pubmed_id': 14681369,
            },
        ],
        'imported': True,
    },
    {
        'name': 'SRPDB',
        'label': 'srpdb',
        'url': 'http://rnp.uthscsa.edu/rnp/SRPDB/SRPDB.html',
        'description': 'provides aligned, annotated and phylogenetically ordered sequences related to structure and function of SRP',
        'abbreviation': 'Signal Recognition Particle Database',
        'examples': ['URS00000478B7', 'URS00001C03DC', 'URS00005C64FE'],
        'references': [
            {
                'title': 'Kinship in the SRP RNA family',
                'authors': 'Rosenblad MA., Larsen N., Samuelsson T., Zwieb C.',
                'journal': 'RNA Biol 6(5): 508-516 (2009 Nov-Dec)',
                'pubmed_id': 19838050,
            },
            {
                'title': 'The tmRDB and SRPDB resources',
                'authors': 'Andersen ES., Rosenblad MA., Larsen N., Westergaard JC., Burks J., Wower IK., Wower J., Gorodkin J., Samuelsson T., Zwieb C.',
                'journal': 'Nucleic Acids Res. 34(Database issue): D163-8 (2006 Jan)',
                'pubmed_id': 16381838,
            },
        ],
        'imported': True,
    },
    {
        'name': 'lncRNAdb',
        'label': 'lncrnadb',
        'url': 'http://lncrnadb.org/',
        'description': 'is a database providing comprehensive annotations of eukaryotic long non-coding RNAs (lncRNAs)',
        'abbreviation': '',
        'examples': ['URS00000478B7', 'URS00005E1511', 'URS0000147018'],
        'references': [
            {
                'title': 'lncRNAdb: a reference database for long noncoding RNAs',
                'authors': 'Amaral P.P., Clark M.B., Gascoigne D.K., Dinger M.E., Mattick J.S.',
                'journal': 'Nucleic Acids Res. 39(Database issue):D146-D151(2011)',
                'pubmed_id': '21112873',
            },
        ],
        'imported': True,
    },
    {
        'name': 'gtRNAdb',
        'label': 'gtrnadb',
        'url': 'http://gtrnadb.ucsc.edu/',
        'description': 'contains tRNA gene predictions on complete or nearly complete genomes',
        'abbreviation': '',
        'examples': ['URS000047C79B', 'URS00006725C9', 'URS00001F9D54'],
        'references': [
            {
                'title': 'GtRNAdb: a database of transfer RNA genes detected in genomic sequence',
                'authors': 'Chan P.P., Lowe T.M.',
                'journal': 'Nucleic Acids Res. 37(Database issue):D93-D97(2009)',
                'pubmed_id': 18984615,
            },
        ],
        'imported': True,
    },
    {
        'name': 'RefSeq',
        'label': 'refseq',
        'url': 'http://www.ncbi.nlm.nih.gov/refseq/',
        'description': 'is a comprehensive, integrated, non-redundant, well-annotated set of reference sequences',
        'abbreviation': 'NCBI Reference Sequence Database',
        'examples': ['URS000075A3E5', 'URS000075ADFF', 'URS00003A96B7'],
        'references': [
            {
                'title': 'RefSeq: an update on mammalian reference sequences.',
                'authors': 'Pruitt K.D., Brown G.R., Hiatt S.M., Thibaud-Nissen F., Astashyn A., Ermolaeva O., Farrell C.M., Hart J., Landrum M.J., McGarvey K.M. et al.',
                'journal': 'Nucleic Acids Res. 2014 Jan;42(Database issue):D756-63',
                'pubmed_id': '24259432',
            },
        ],
        'imported': True,
    },
    {
        'name': 'RDP',
        'label': 'rdp',
        'url': 'http://rdp.cme.msu.edu/',
        'description': 'provides quality-controlled, aligned and annotated rRNA sequences and a suite of analysis tools',
        'abbreviation': 'Ribosomal Database Project',
        'examples': ['URS000064300F', 'URS00006FBF68', 'URS000070C439'],
        'references': [
            {
                'title': 'Ribosomal Database Project: data and tools for high throughput rRNA analysis',
                'authors': 'Cole J.R., Wang Q., Fish J.A., Chai B., McGarrell D.M., Sun Y., Brown C.T., Porras-Alfaro A., Kuske C.R., Tiedje J.M.',
                'journal': 'Nucleic Acids Res. 2014 Jan;42(Database issue):D633-42',
                'pubmed_id': '24288368',
            },
        ],
        'imported': True,
    },
    {
        'name': 'CRW Site',
        'label': '',
        'url': 'http://www.rna.ccbb.utexas.edu/',
        'description': 'comparative sequence and structure information for ribosomal, intron, and other RNAs',
        'abbreviation': 'Comparative RNA Website',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'HGNC',
        'label': '',
        'url': 'http://www.genenames.org/',
        'description': 'HUGO Gene Nomenclature Committee',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'GreenGenes',
        'label': '',
        'url': 'http://greengenes.secondgenome.com/downloads',
        'description': '16S rRNA gene database',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'LncBase',
        'label': '',
        'url': 'http://www.microrna.gr/LncBase',
        'description': 'experimentally verified and computationally predicted microRNA targets on long non-coding RNAs',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'LNCipedia',
        'label': '',
        'url': 'http://www.lncipedia.org/',
        'description': 'a comprehensive compendium of human long non-coding RNAs',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'MODOMICS',
        'label': '',
        'url': 'http://modomics.genesilico.pl/',
        'description': 'RNA modification data',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'NONCODE',
        'label': '',
        'url': 'http://www.noncode.org/',
        'description': 'integrative annotation of long noncoding RNAs',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'NPInter',
        'label': '',
        'url': 'http://bioinfo.ibp.ac.cn/NPInter/',
        'description': 'experimentally determined functional interactions between ncRNAs and proteins, mRNAs or genomic DNA',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'piRNABank',
        'label': '',
        'url': 'http://pirnabank.ibab.ac.in/',
        'description': 'comprehensive resource on Piwi-interacting RNAs',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'PLncDB',
        'label': '',
        'url': 'http://chualab.rockefeller.edu/gbrowse2/homepage.html',
        'description': 'plant long noncoding RNA Database',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'PomBase',
        'label': '',
        'url': 'http://www.pombase.org/',
        'description': 'the scientific resource for fission yeast',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'RNApathwaysDB',
        'label': '',
        'url': 'http://genesilico.pl/rnapathwaysdb',
        'description': 'RNA maturation and decay pathways',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'SILVA',
        'label': '',
        'url': 'http://www.arb-silva.de/',
        'description': 'quality checked and aligned ribosomal RNA sequences',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'SGD',
        'label': '',
        'url': 'http://yeastgenome.org/',
        'description': 'provides comprehensive integrated biological information for the budding yeast',
        'abbreviation': 'Saccharomyces Genome Database',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'snOPY',
        'label': 'snopy',
        'url': 'http://snoopy.med.miyazaki-u.ac.jp',
        'description': 'provides comprehensive information about snoRNAs, snoRNA gene loci, and target RNAs',
        'abbreviation': 'snoRNA Orthological Gene Database',
        'examples': ['URS0000456CE0', 'URS00005CC29F', 'URS0000817CAB'],
        'references': [
            {
                'title': 'snOPY: a small nucleolar RNA orthological gene database',
                'authors': 'Yoshihama M., Nakao A., Kenmochi N.',
                'journal': 'BMC Res Notes 6:426-426(2013)',
                'pubmed_id': '24148649',
            },
        ],
        'imported': True,
    },
    {
        'name': 'snoRNA Database',
        'label': '',
        'url': 'http://lowelab.ucsc.edu/snoRNAdb/',
        'description': 'predicted snoRNA genes',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'sRNAmap',
        'label': '',
        'url': 'http://srnamap.mbc.nctu.edu.tw/',
        'description': 'a collection of sRNA sequences and interactions',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'TarBase',
        'label': '',
        'url': 'http://www.microrna.gr/tarbase',
        'description': 'a collection of manually curated experimentally validated miRNA-gene interactions',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'tmRDB',
        'label': '',
        'url': 'http://rth.dk/resources/rnp/tmRDB/',
        'description': 'aligned, annotated and phylogenetically ordered sequences related to structure and function of tmRNA',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'tRNAdb',
        'label': '',
        'url': 'http://trna.bioinf.uni-leipzig.de/DataOutput/',
        'description': 'compilation of tRNA sequences and tRNA genes',
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
    {
        'name': 'WormBase',
        'label': '',
        'url': 'http://www.wormbase.org/',
        'description': "the world's repository for nematode biology",
        'abbreviation': '',
        'examples': '',
        'references': [],
        'imported': False,
    },
]
