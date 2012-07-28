'use strict';

/* Services */

angular.module('cellar.services', ['ngResource']).
    factory('Wine', function($resource) {
        var res = $resource('/rest/cellar/wines/:id', {'id': '@_id'}, {
            //'id': '@_id'
            'list':   {method: 'GET', params:{'id': ''}, isArray:true},
            'create': {method: 'POST'},
            'update': {method: 'PUT'},  
            'remove': {method: 'DELETE'}
        });

        res.prototype.$remove = function(cb) {
            return res.$remove({'id': this._id}, cb);
        };

        // res.prototype.create = function(cb) {
        //     return res.create({'id': this._id}, cb);
        // };

        return res;
    });
