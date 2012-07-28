'use strict';

/* Controllers */

function MenuCtrl($scope, $location) {
    $scope.addWine = function () {
        $location.path('/wines/new');
    };
}


function WineListCtrl($scope, Wine) {
    $scope.wines = Wine.list();
}


function WineDetailsCtrl($scope, $location, $routeParams, Wine) {
    if ($routeParams.wineId === 'new') {
        $scope.wine = new Wine();
    } else {
        $scope.wine = Wine.get({id: $routeParams.wineId});
    }
    $scope.addWine = function () {
            $location.path('/wines/new');
    };

    $scope.saveWine = function () {
        if ($scope.wine._id === undefined)
            $scope.wine.$create($scope.wine, function(wine) {
                $location.path('/wines/' + wine._id);
            });
        else
            $scope.wine.$update($scope.wine, function(wine) {
                //window.location = "#/wines/" + wine._id;
                $location.path('/wines/' + wine._id);
            });
    };

    $scope.deleteWine = function () {
        $scope.wine.$destroy($scope.wine, function() {
            //alert('Wine ' + this.wine.name + ' deleted');
            $location.path('/wines');
        });
    };

}
