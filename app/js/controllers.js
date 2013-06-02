'use strict';
/* Controllers */

function SupercarListCtrl($scope, $location, Supercars) {
    $scope.supercars = Supercars.list();

    $scope.addSupercar = function () {
        $location.path('/supercars/new');
    };
}


function SupercarDetailsCtrl($scope, $location, $routeParams, Supercars) {
    // nested controller to SupercarListCtrl so it can do updates
    if ($routeParams.supercarId === 'new') {
        $scope.supercar = new Supercars(); 
    } else {
        $scope.supercar = Supercars.get({id: $routeParams.supercarId});
    }

    $scope.saveSupercar = function () {
        if ($scope.supercar._id === undefined)
            $scope.supercar.$save(function(supercar) {
                // update the supercar list in the parent scope
                $scope.$parent.supercars = Supercars.list();
                $location.path('/supercars/' + supercar._id);
            });
        else
            $scope.supercar.$update(function(supercar) {
                // update the list since the name might have been changed
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