'use strict';

/* Controllers */

function SupercarListCtrl($scope, $location, Wine) {
    $scope.supercars = Wine.list();

    $scope.addSupercar = function () {
        $location.path('/supercars/new');
    };
}


function SupercarDetailsCtrl($scope, $location, $routeParams, Wine) {
    // nested controller to SupercarListCtrl so it can do updates
    if ($routeParams.supercarId === 'new') {
        $scope.supercars = new Supercars(); 
    } else {
        $scope.supercars = Supercars.get({id: $routeParams.supercarId});
    }

    $scope.saveSupercar = function () {
        if ($scope.supercar._id === undefined)
            $scope.supercar.$save(function(wine) {
                // update the supercar list in the parent scope
                $scope.$parent.supercars = Supercars.list();
                $location.path('/supercars/' + supercar._id);
            });
        else
            $scope.supercar.$update(function(wine) {
                // update the list since it is possible to update the name
                $scope.$parent.supercars = Supercars.list();
                $location.path('/supercars/' + supercar._id);
            });
    };

    $scope.deleteSupercar = function () {
        $scope.supercar.$remove(function() {
            // update the supercar list in the parent scope
            $scope.$parent.supercars = Supercars.list();
            $location.path('/supercars');
        });
    };
}
