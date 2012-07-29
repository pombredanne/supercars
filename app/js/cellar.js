'use strict';


// Declare app level module which depends on filters, and services
angular.module('cellar', ['cellar.filters', 'cellar.services']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/wines', {templateUrl: 'partials/welcome.html'});
        $routeProvider.when('/wines/:wineId', {templateUrl: 'partials/wine-details.html',
            controller: WineDetailsCtrl});
        $routeProvider.otherwise({redirectTo: '/wines'});
}]);

