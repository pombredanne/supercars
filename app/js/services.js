'use strict';

/* Services */


angular.module('cellar.services', ['ngResource']).
    factory('Wine', function($resource) {
        return $resource('/rest/cellar/wines/:id', {},
            {get_all: {method: 'GET', params:{'id': ''}, isArray:true}
        });
    });
