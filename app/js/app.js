'use strict';


// Declare app level module which depends on filters, and services
angular.module('cellar', ['cellar.filters', 'cellar.services', 'cellar.directives']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/wines', {template: 'partials/welcome.html',
            controller: WineListCtrl});
        $routeProvider.when('/wines/:wineId', {template: 'partials/wine-details.html', controller: WineDetailsCtrl});
        $routeProvider.otherwise({redirectTo: '/wines'});
  }]);

/*
// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/view1', {template: 'partials/welcome.html', controller: MyCtrl1});
    $routeProvider.when('/view2', {template: 'partials/partial2.html', controller: MyCtrl2});
    $routeProvider.otherwise({redirectTo: '/view1'});
  }]);
  */