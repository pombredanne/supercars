'use strict';

/* Controllers */

function WineListCtrl($scope, $location, Wine) {
    $scope.wines = Wine.list();

    $scope.addWine = function () {
        $location.path('/wines/new');
    };
}


function WineDetailsCtrl($scope, $location, $routeParams, Wine) {
    // nested controller to WineListCtrl so it can do updates
    // using $scope.$parent.foo = 'bar'
    if ($routeParams.wineId === 'new') {
        $scope.wine = new Wine();
    } else {
        $scope.wine = Wine.get({id: $routeParams.wineId});
    }

    $scope.saveWine = function () {
        if ($scope.wine._id === undefined)
            $scope.wine.$save(function(wine) {
                // update the wine list in the parent scope
                $scope.$parent.wines = Wine.list();
                $location.path('/wines/' + wine._id);
            });
        else
            $scope.wine.$update(function(wine) {
                $location.path('/wines/' + wine._id);
            });
    };

    $scope.deleteWine = function () {
        $scope.wine.$remove(function() {
            // update the wine list in the parent scope
            $scope.$parent.wines = Wine.list();
            $location.path('/wines');
        });
    };

}
