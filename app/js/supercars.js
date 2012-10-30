'use strict';


// Declare app level module which depends on filters, and services
angular.module('supercars', ['supercars.filters', 'supercars.services']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/supercars', {templateUrl: 'partials/welcome.html'});
        $routeProvider.when('/supercars/:wineId', {templateUrl: 'partials/supercar-details.html',
            controller: SupercarDetailsCtrl});
        $routeProvider.otherwise({redirectTo: '/supercars'});
}]);

