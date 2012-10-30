'use strict';

/* Services */

angular.module('supercars.services', ['ngResource']).
    factory('Wine', function($resource) {
        var Wine = $resource('/rest/supercars/:id', {'id': '@_id'}, {
            'list':   {method: 'GET', params:{'id': ''}, isArray:true},
          'update': {method: 'PUT'}
        });

        return Wine;
    });
