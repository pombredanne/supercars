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

    $scope.saveWine = function () {
        if ($scope.wine._id === undefined)
            $scope.wine.$save(function(wine) {
                $location.path('/wines/' + wine._id);
            });
        else
            $scope.wine.$update(function(wine) {
                $location.path('/wines/' + wine._id);
            });
    };

    $scope.deleteWine = function () {
        $scope.wine.$remove(function() {
            //alert('Wine ' + this.wine.name + ' deleted');
            // update the wine list as well
            $scope.wines = Wine.list(function() {
                $location.path('/wines');
            });
        });
    };

}


scope tip:

"you may need to do something like $scope.foo = $scope.$parent.foo = 'bar"'   