'use strict';

/* Services */


angular.module('cellar.services', ['ngResource']).
    factory('Wine', function($resource) {
        return $resource('/rest/cellar/wines/:id', {}, {
            'list': {method: 'GET', params:{'id': ''}, isArray:true},
            'create': {method: 'POST'},
            'update': {method: 'PUT'},
            'delete': {method: 'DELETE'}
        });
    });
