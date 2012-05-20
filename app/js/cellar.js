'use strict';


// Declare app level module which depends on filters, and services
var module = angular.module('cellar', ['cellar.filters', 'cellar.services', 'cellar.directives']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/wines', {template: 'partials/welcome.html',
            controller: WineListCtrl});
        $routeProvider.when('/wines/:wineId', {template: 'partials/wine-details.html',
            controller: WineDetailsCtrl});
        $routeProvider.otherwise({redirectTo: '/wines'});
}]);

