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

from portal.models import Rna, Accession
from rest_framework import generics
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from apiv1.serializers import RnaNestedSerializer, AccessionSerializer, CitationSerializer, XrefSerializer, RnaFlatSerializer
import django_filters
import re


class RnaFilter(django_filters.FilterSet):
    min_length = django_filters.NumberFilter(name="length", lookup_type='gte')
    max_length = django_filters.NumberFilter(name="length", lookup_type='lte')
    external_id = django_filters.CharFilter(name="xrefs__accession__external_id", distinct=True)

    class Meta:
        model = Rna
        fields = ['upi', 'md5', 'length', 'min_length', 'max_length', 'external_id']


class APIRoot(APIView):
    """
    This is the root of the RNAcentral API Version 1.

    [API documentation](/api)
    """
    # the above docstring appears on the API root web page
    permission_classes = (AllowAny,)

    def get(self, request, format=format):
        return Response({
            'rna': reverse('rna-list', request=request),
        })


def _flat_or_nested_rna_serializer(obj):
    """
    """
    flat = obj.request.QUERY_PARAMS.get('flat', 'false')
    if re.match('true', flat, re.IGNORECASE):
        return RnaFlatSerializer
    return RnaNestedSerializer


class RnaList(generics.ListAPIView):
    """
    RNA Sequences

    [API documentation][ref]
    [ref]: /api
    """
    # the above docstring appears on the API root web page
    permission_classes = (AllowAny,)
    filter_class = RnaFilter

    def get_serializer_class(self):
        return _flat_or_nested_rna_serializer(self)

    def _get_database_id(self):
        """
        Map the `database` parameter from the url to internal database ids
        """
        database = self.request.QUERY_PARAMS.get('database', None)
        if not database:
            pass
        elif re.match('ena', database, re.IGNORECASE):
            database = 1
        elif re.match('rfam', database, re.IGNORECASE):
            database = 2
        elif re.match('srpdb', database, re.IGNORECASE):
            database = 3
        elif re.match('mirbase', database, re.IGNORECASE):
            database = 4
        elif re.match('vega', database, re.IGNORECASE):
            database = 5
        elif re.match('tmrna_website', database, re.IGNORECASE):
            database = 6
        return database

    def get_queryset(self):
        """
        Manually filter against the `database` query parameter,
        use RnaFilter for other filtering operations.
        """
        queryset = Rna.objects.defer('seq_short', 'seq_long').select_related().all()
        database = self._get_database_id()
        if database:
            queryset = queryset.filter(xrefs__db=database)
        return queryset


class RnaDetail(generics.RetrieveAPIView):
    """
    Unique RNAcentral Sequence
    """
    # the above docstring appears on the API root web page
    queryset = Rna.objects.select_related().all()

    def get_serializer_class(self):
        return _flat_or_nested_rna_serializer(self)


class XrefList(generics.ListAPIView):
    queryset = Rna.objects.select_related().all()
    serializer_class = RnaNestedSerializer

    def get(self, request, pk=None, format=format):
        """
        Retrieve cross-references for a particular RNA sequence.
        """
        rna = self.get_object()
        xrefs = rna.xrefs.all()
        serializer = XrefSerializer(xrefs, context={'request': request})
        return Response(serializer.data)


class FastaRenderer(renderers.BaseRenderer):
    media_type = 'text/fasta'
    format = 'fasta'

    def render(self, rna, media_type=None, renderer_context=None):
        """
        Split long sequences by a fixed number of characters per line.
        """
        max_column = 80
        seq = rna.get_sequence()
        split_seq = ''
        i = 0
        while i < len(seq):
            split_seq += seq[i:i+max_column] + "\n"
            i += max_column
        fasta = "> %s\n%s" % (rna.upi, split_seq)
        return fasta


class RnaFastaView(generics.RetrieveAPIView):
    """
    Render RNA sequence in fasta format.
    """
    queryset = Rna.objects.all()
    renderer_classes = [FastaRenderer]

    def get(self, request, pk, format=None):
        """
        Retrive the Rna object and pass it on to the renderer.
        """
        rna = self.get_object()
        return Response(rna)


class AccessionView(generics.RetrieveAPIView):
    """
    API endpoint that allows single accessions to be viewed.

    [API documentation][ref]
    [ref]: /api
    """
    # the above docstring appears on the API root web page
    queryset = Accession.objects.select_related().all()
    serializer_class = AccessionSerializer

    def get(self, request, pk, format=None):
        """
        Retrive individual accessions.
        """
        accession = self.get_object()
        serializer = AccessionSerializer(accession, context={'request': request})
        return Response(serializer.data)


class CitationView(generics.RetrieveAPIView):
    """
    API endpoint that allows the citations associated with
    each cross-reference to be viewed.

    [API documentation][ref]
    [ref]: /api
    """
    queryset = Accession.objects.select_related().all()

    def get(self, request, *args, **kwargs):
        """
        Retrieve citations associated with a particular entry.
        This method is used to retrieve citations for the unique sequence view.
        """
        accession = self.get_object()
        citations = accession.refs.all()
        serializer = CitationSerializer(citations)
        return Response(serializer.data)

