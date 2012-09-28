'use strict';

/* jasmine specs for controllers go here */
describe('Ajaxdemo controllers', function() {

  beforeEach(function(){
    this.addMatchers({
      toEqualData: function(expected) {
        return angular.equals(this.actual, expected);
      }
    });
  });

beforeEach(module('cellar.services'));


  describe('WineListCtrl', function() {
    var scope, ctrl, $httpBackend;

    beforeEach(inject(function(_$httpBackend_, $rootScope, $controller) {
      $httpBackend = _$httpBackend_;
      $httpBackend.expectGET('/rest/cellar/wines').
          respond([
            {"name":"BLOCK NINE","year":"2009","grapes":"Pinot Noir","country":"USA","region":"California","description":"With hints of ginger and spice, this wine makes an excellent complement to light appetizer and dessert fare for a holiday gathering."},
            {"name":"BODEGA LURTON","year":"2011","grapes":"Pinot Gris","country":"Argentina","region":"Mendoza","description":"Solid notes of black currant blended with a light citrus make this wine an easy pour for varied palates."}]);

      scope = $rootScope.$new();
      ctrl = $controller(WineListCtrl, {$scope: scope});
    }));


    it('should create "wines" model containing 2 wines fetched from backend', function() {
      expect(scope.wines).toEqual([]);
      $httpBackend.flush();

      expect(scope.wines).toEqualData([
            {"name":"BLOCK NINE","year":"2009","grapes":"Pinot Noir","country":"USA","region":"California","description":"With hints of ginger and spice, this wine makes an excellent complement to light appetizer and dessert fare for a holiday gathering."},
            {"name":"BODEGA LURTON","year":"2011","grapes":"Pinot Gris","country":"Argentina","region":"Mendoza","description":"Solid notes of black currant blended with a light citrus make this wine an easy pour for varied palates."}]);
    });

  });

});
