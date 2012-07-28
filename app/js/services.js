'use strict';

/* Services */

angular.module('cellar.services', ['ngResource']).
    factory('Wine', function($resource) {
        var res = $resource('/rest/cellar/wines/:id', {'id': '@_id'}, {
            //'id': '@_id'
            'list':   {method: 'GET', params:{'id': ''}, isArray:true},
            'create': {method: 'POST'},
            'update': {method: 'PUT'},
            'destroy': {method: 'DELETE'}
        });

        res.prototype.destroy = function(cb) {
            return res.destroy({'id': this._id}, cb); //'_id': this._id
        };

        return res;
    });
