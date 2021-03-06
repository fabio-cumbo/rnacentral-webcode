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

import datetime

from django.core.urlresolvers import reverse
from django.db import connections
from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.cache import never_cache

from .settings import MIN_LENGTH, MAX_LENGTH, RQDASHBOARD
from .messages import messages
from .utils import get_job, enqueue_job, nhmmer_proxy, kill_nhmmer_job
from .models import Results, Query

from rest_framework import generics, serializers, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes


@never_cache
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def submit_job(request):
    """
    Start nhmmer search.

    HTTP responses:
    * 201 - job submitted
    * 400 - incorrect input
    * 500 - internal error
    """
    proxy_result = nhmmer_proxy(request)
    if proxy_result:
        return proxy_result

    msg = messages['submit']

    if request.method == 'POST':
        query = request.POST.get('q', '')
        description = request.POST.get('description', '')
    elif request.method == 'GET':
        query = request.GET.get('q', '')
        description = request.GET.get('description', '')

    if not query:
        status = 400
        return Response(msg[status]['no_sequence'], status=status)

    if len(query) < MIN_LENGTH:
        status = 400
        return Response(msg[status]['too_short'], status=status)
    elif len(query) > MAX_LENGTH:
        status = 400
        return Response(msg[status]['too_long'], status=status)

    try:
        status = 201
        job_id = enqueue_job(query, description)
        url = request.build_absolute_uri(
            reverse('nhmmer-job-status') +
            '?id=%s' % job_id
        )
        data = {
            'id': job_id,
            'url': url,
        }
        return Response(data, status=status)
    except:
        status = 500
        return Response(msg[status], status=status)


@never_cache
@api_view(['GET'])
@permission_classes([AllowAny])
def cancel_job(request):
    """
    Cancel nhmmer search.

    HTTP responses:
    * 200 - job cancelled
    * 400 - incorrect input
    * 500 - internal error
    """
    proxy_result = nhmmer_proxy(request)
    if proxy_result:
        return proxy_result

    msg = messages['cancel']

    job_id = request.GET.get('id', '')
    if not job_id:
        status = 400
        return Response(msg[status], status=status)

    try:
        # cancel job
        job = get_job(job_id)[0]
        job.cancel()
        # kill nhmmer process
        kill_nhmmer_job(job_id)
        # set query `finished` field
        query = Query.objects.get(id=job_id)
        query.finished = datetime.datetime.now()
        query.save()
        status = 200
        return Response(msg[status], status=status)
    except:
        status = 500
        return Response(msg[status], status=status)


class StatusSerializer(serializers.Serializer):
    """
    Serializer class for job status.
    """
    id = serializers.CharField()
    status = serializers.CharField()
    enqueued_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField()
    expiration = serializers.DateTimeField()
    url = serializers.CharField()


@never_cache
@api_view(['GET'])
@permission_classes([AllowAny])
def get_status(request):
    """
    Get status of an nhmmer search.

    HTTP responses:
    * 200 - job found
    * 400 - job id not provided in the url
    * 404 - job not found in the queue
    * 500 - internal error
    """
    proxy_result = nhmmer_proxy(request)
    if proxy_result:
        return proxy_result

    msg = messages['status']

    job_id = request.GET.get('id', '')
    if not job_id:
        status = 400
        return Response(msg[status], status=status)

    try:
        job = get_job(job_id)[0]
        if job:
            url = request.build_absolute_uri(
                reverse('nhmmer-job-results') +
                '?id=%s' % job_id
            )
            return Response(StatusSerializer({
                'id': job.id,
                'status': job.get_status(),
                'enqueued_at': job.enqueued_at,
                'ended_at': job.ended_at,
                'expiration': job.meta.get('expiration', None),
                'url': url,
            }).data)
        else:
            status = 404
            return Response(msg[status], status=status)
    except:
        status = 500
        return Response(msg[status], status=status)


class ResultsSerializer(serializers.ModelSerializer):
    """
    Django Rest Framework serializer class for
    listing nhmmer search results.
    """
    id = serializers.CharField(source='result_id')
    rnacentral_id = serializers.CharField()
    description = serializers.CharField()
    bias = serializers.FloatField()
    target_length = serializers.IntegerField()
    query_length = serializers.IntegerField()
    alignment = serializers.CharField()
    score = serializers.FloatField()
    e_value = serializers.FloatField()
    nts_count1 = serializers.IntegerField()
    nts_count2 = serializers.IntegerField()

    class Meta:
        model = Results
        fields = ('id', 'rnacentral_id', 'description', 'bias',
                  'target_length', 'query_length', 'alignment',
                  'score', 'e_value', 'match_count', 'gap_count',
                  'alignment_length', 'nts_count1', 'nts_count2',
                  'identity', 'query_coverage', 'target_coverage',
                  'gaps')


class ResultsView(generics.ListAPIView):
    """
    Django Rest Framework Generic View class
    for listing Nhmmer results based on query id.
    """
    permission_classes = (AllowAny,)
    serializer_class = ResultsSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('identity', 'query_coverage', 'target_coverage',
                       'gaps', 'e_value', 'result_id')
    ordering = ('e_value', 'result_id') # default ordering

    def get_queryset(self):
        """
        Filter results by query id.
        """
        query_id = self.request.query_params.get('id', None)
        return Results.objects.filter(query_id=query_id)


class QuerySerializer(serializers.ModelSerializer):
    """
    Django Rest Framework serializer class for
    retrieving query details.
    """
    id = serializers.CharField()
    sequence = serializers.CharField(source='query')
    length = serializers.ReadOnlyField(source='get_length')
    description = serializers.CharField()
    enqueued_at = serializers.DateTimeField(source='submitted')
    ended_at = serializers.DateTimeField(source='finished')

    class Meta:
        model = Query
        fields = ('id', 'sequence', 'length', 'description',
                  'enqueued_at', 'ended_at')


class QueryView(generics.RetrieveAPIView):
    """
    Django Rest Framework view class for retrieving
    query details.
    """
    permission_classes = (AllowAny,)
    serializer_class = QuerySerializer

    def get_object(self):
        """
        Retrieve Query object.
        """
        query_id = self.request.query_params.get('id', None)
        return get_object_or_404(Query, pk=query_id)


@never_cache
def dashboard_view(request):
    """
    Dashboard showing the status of sequence search.
    """
    def dictfetchall(cursor):
        """
        Return all rows from a cursor as a dict
        """
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def get_queries_over_time(cursor):
        """
        Get the number of queries aggregated by date.
        """
        cmd = """
        SELECT DATE_FORMAT(submitted, "%d-%m-%y") as date, count(*) as total
        FROM nhmmer_query
        GROUP BY DATE_FORMAT(submitted, "%d-%m-%y")
        ORDER BY submitted
        """
        cursor.execute(cmd, None)
        return dictfetchall(cursor)

    def get_db_size(cursor):
        """
        Get nhmmer search results database size.
        """
        schema = 'nhmmer_results'
        cmd = """
        SELECT sum( data_length + index_length ) "size"
        FROM information_schema.TABLES
        WHERE table_schema = '{0}' GROUP BY table_schema
        """.format(schema)
        cursor.execute(cmd, None)
        return dictfetchall(cursor)

    cursor = connections['nhmmer_db'].cursor()
    db_size = get_db_size(cursor)

    context = {
        'total_queries': Query.objects.count(),
        'data': get_queries_over_time(cursor),
        'db_size': db_size[0]['size'],
        'db_percent': 100 - (db_size[0]['size']/500000000000)*100,
        'oldest_query': Query.objects.order_by('submitted').first(),
        'rqdashboard': RQDASHBOARD,
    }
    return render_to_response('nhmmer/dashboard.html', {"context": context})
