'use strict';

/* Controllers */

function WineListCtrl($scope, Wine) {
    $scope.wines = Wine.list();
}


function WineDetailsCtrl($scope, $routeParams, Wine) {
    if ($routeParams.wineId === 'new') {
        $scope.wine = new Wine();
    } else {
        $scope.wine = Wine.get({id: $routeParams.wineId});
    }
    $scope.addWine = function () {
        window.location = "#/wines/add";
    };

    $scope.saveWine = function () {
        if (this.wine._id === undefined)
            this.wine.$create();
        else
            this.wine.$update({id:this.wine._id}, function() {
                window.location = "#/wines";
            });
    };

    $scope.deleteWine = function () {
        this.wine.$delete({id:this.wine._id}, function() {
            //alert('Wine ' + this.wine.name + ' deleted');
            window.location = "#/wines";
        });
    };

}
