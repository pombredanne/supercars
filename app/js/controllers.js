'use strict';

/* Controllers */


function WineListCtrl($scope, Wine) {
    $scope.wines = Wine.get_all();
}


function WineDetailsCtrl($scope, $routeParams, Wine) {
    $scope.wine = Wine.get({id: $routeParams.wineId});
}
