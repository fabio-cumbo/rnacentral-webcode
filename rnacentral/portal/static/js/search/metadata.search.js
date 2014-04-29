/*
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
*/

// RNAcentral metasearch app.

;

/**
 * Make it possible to include underscore as a dependency.
 */
var underscore = angular.module('underscore', []);
underscore.factory('_', function() {
    return window._;
});

/**
 * Create RNAcentral app.
 */
var rnaMetasearch = angular.module('rnacentralApp', ['chieffancypants.loadingBar', 'underscore']);

/**
 * html5mode removes hashtags from urls.
 */
rnaMetasearch.config(['$locationProvider', function($locationProvider) {
    $locationProvider.html5Mode(true);
}]);

/**
 * Service for passing data between controllers.
 */
rnaMetasearch.service('results', ['_', function(_) {
    var result = {
        'hits': null,
        'rnas': []
    }
    var show_results = false;

    /**
     * Process deeply nested json objects like this:
     * { "field" : [ {"id": "description", "values": {"value": "description_value"}} ] }
     * into key-value pairs like this:
     * {"description": "description_value"}
     */
    function preprocess_results(data) {
        result.hits = data.result.hitCount;
        result.rnas = _.each(data.result.entries.entry, function(entry){
            _.each(entry.fields.field, function(field){
                entry[field['@id']] = field.values.value;
            });
        });
    };

    return {
        get_status: function() {
            return show_results;
        },
        set_status: function() {
            show_results = true;
        },
        save_results: function(data) {
            preprocess_results(data);
            console.log(result);
        },
        get_results: function() {
            return result;
        }
    }
}]);

rnaMetasearch.controller('MainContent', ['$scope', '$anchorScroll', '$location', 'results', function($scope, $anchorScroll, $location, results) {
    /**
     * Enables scrolling to anchor tags.
     * <a ng-click="scrollTo('anchor')">Title</a>
     */
    $scope.scrollTo = function(id) {
        $location.hash(id);
        $anchorScroll();
    };

    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results = newValue;
        }
    });
}]);

rnaMetasearch.controller('ResultsListCtrl', ['$scope', 'results', function($scope, results) {

    $scope.result = results.get_results();
    $scope.show_results = results.get_status();

    $scope.$watch(function () { return results.get_results(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.result = newValue;
        }
    });

    $scope.$watch(function () { return results.get_status(); }, function (newValue, oldValue) {
        if (newValue != null) {
            $scope.show_results = newValue;
        }
    });

}]);

rnaMetasearch.controller('QueryCtrl', ['$scope', '$http', '$location', 'results', function($scope, $http, $location, results) {

    $scope.query = {
        text: '',
        submitted: false
    };
    $scope.show_results = false;
    $scope.save_results = results.save_results;
    $scope.set_status = results.set_status;

    var ebeye_base_url = 'http://ash-4.ebi.ac.uk:8080';
    var fields = ['description', 'active', 'length', 'name'];
    var query_urls = {
        'ebeye_search': ebeye_base_url + '/ebisearch/ws/rest/rnacentral' +
                                         '?query={QUERY}' +
                                         '&format=json' +
                                         '&fields=' + fields.join(),
        'proxy': 'http://localhost:8000/api/internal/ebeye?url={EBEYE_URL}'
    };

    // watch url changes to perform a new search
    $scope.$watch(function () { return $location.url(); }, function (newUrl, oldUrl) {

         // a regular non-search url, potentially unchanged
        if (newUrl !== oldUrl) {
            if (newUrl.indexOf('/search') == -1) {
                // not a search page, redirect
                window.location.href = newUrl;
            } else {
                // a search result page, launch a new search
                $scope.query.text = $location.search().q;
                $scope.search($location.search().q);
            }
        }
    });

    $scope.search = function(query) {
        $scope.query.text = query;
        $scope.show_results = true;
        $scope.set_status();
        $location.url('/search' + '?q=' + query);

        var ebeye_url = query_urls.ebeye_search.replace('{QUERY}', query);
        var url = query_urls.proxy.replace('{EBEYE_URL}', encodeURIComponent(ebeye_url));

        $http({
            url: url,
            method: 'GET'
        }).success(function(data) {
            $scope.save_results(data);
            $scope.query.submitted = false;
        });
    }

    $scope.submit_query = function() {
        $scope.query.submitted = true;
        if ($scope.queryForm.text.$invalid) {
            return;
        }
        $scope.search($scope.query.text);
    };

    var check_if_search_url = function () {
       // check if there is query in url
        if ($location.url().indexOf("/search?q=") > -1) {
            // a search result page, launch a new search
            $scope.query.text = $location.search().q;
            $scope.search($location.search().q);
        }
    };

    // run once at initialisation
    check_if_search_url();
}]);
