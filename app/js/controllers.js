'use strict';

/* Controllers */


//function WineListCtrl() {}
function WineListCtrl($scope, Wine) {
    $scope.wines = Wine.get_all();
    // $scope.wines = [
    //     {"id":"9","name":"BLOCK NINE"},
    //     {"id":"11","name":"BODEGA LURTON"},
    //     {"id":"1","name":"CHATEAU DE SAINT COSME"},
    //     {"id":"7","name":"CHATEAU LE DOYENNE"},
    //     {"id":"8","name":"DOMAINE DU BOUSCAT"},
    //     {"id":"10","name":"DOMAINE SERENE"},
    //     {"id":"2","name":"LAN RIOJA CRIANZA"},
    //     {"id":"12","name":"LES MORIZOTTES"},
    //     {"id":"3","name":"MARGERUM SYBARITE"},
    //     {"id":"4","name":"OWEN ROE \"EX UMBRIS\""},
    //     {"id":"5","name":"REX HILL"},
    //     {"id":"6","name":"VITICCIO CLASSICO RISERVA"}
    // ];
}




function WineDetailsCtrl($scope, Wine) {
    $scope.wine = {
"id":"9","name":"BLOCK NINE"
,"year":"2009","grapes":"Pinot Noir","country":"USA","region":"California","description":"With hints of ginger and spice, this wine makes an excellent complement to light appetizer and dessert fare for a holiday gathering.","picture":"block_nine.jpg"};
    //$scope.wine = Wine.get();
    //
    //$scope.wine = Wine.get({wineId: 'wine'});

    //$scope.wine = Wine.get({wineId: $routeParams.wineId}, function(wine) {
    // $scope.wine = Wine.query();
    //$scope.wine = Wine.get({wineId: 'wine'}, function(wine) {
        //$scope.mainImageUrl = phone.images[0];
    //});
}
