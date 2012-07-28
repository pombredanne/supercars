'use strict';

/* Services */

angular.module('cellar.services', ['ngResource']).
    factory('Wine', function($resource) {
        var Wine = $resource('/rest/cellar/wines/:id', {'id': '@_id'}, {
            //'id': '@_id'
            'list':   {method: 'GET', params:{'id': ''}, isArray:true},
            // 'create': {method: 'POST'},
            'update': {method: 'PUT'}
            // 'remove': {method: 'DELETE'}
        });

        // Wine.prototype.create = function(cb) {
        //     return Wine.create({'id': this._id}, cb);
        // };

        // Wine.prototype.update = function(cb) {
        //     return Wine.update({'id': this._id}, cb);
        // };

        // Wine.prototype.remove = function(cb) {
        //     return Wine.remove({'id': this._id}, cb);
        // };

        return Wine;
    });
