'use strict';

/* Services */

angular.module('supercars.services', ['ngResource']).
    factory('Supercars', function($resource) {
        var Supercars = $resource('/rest/supercars/:id', {'id': '@_id'}, {
            'list':   {method: 'GET', params:{'id': ''}, isArray:true},
          'update': {method: 'PUT'}
        });

        return Supercars;
    });
