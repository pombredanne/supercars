'use strict';

/* Services */

angular.module('cellar.services', ['ngResource']).
    factory('Wine', function($resource) {
        var Wine = $resource('/rest/cellar/wines/:id', {'id': '@_id'}, {
            'list':   {method: 'GET', params:{'id': ''}, isArray:true},
          'update': {method: 'PUT'}
        });

        return Wine;
    });
