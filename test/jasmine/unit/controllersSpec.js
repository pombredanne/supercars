'use strict';

/* jasmine specs for controllers go here */
describe('ajaxdemo controllers', function() {
  var scope, location, routeParams, $httpBackend, controller;
  var wineDetails = function() {
      return {
          "name":"BLOCK NINE",
          "year":"2009",
          "grapes":"Pinot Noir",
          "country":"USA"
      };
  };
  var wineList = function() {
    return [{"name":"BLOCK NINE"},{"name":"BODEGA LURTON"}];
  };

  beforeEach(function(){
    this.addMatchers({
      toEqualData: function(expected) {
        return angular.equals(this.actual, expected);
      }
    });
  });

  beforeEach(module('cellar.services'));

  beforeEach(inject(function(_$httpBackend_, $rootScope, $location, $routeParams, $controller) {
    $httpBackend = _$httpBackend_;
    location = $location;
    routeParams = $routeParams;
    scope = $rootScope.$new();
    controller = $controller;
  }));

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation();
    $httpBackend.verifyNoOutstandingRequest();
  });


  describe('WineListCtrl', function() {

    it('should change location when calling addWine', function() {
      $httpBackend.expectGET('/rest/cellar/wines').respond(wineList());
      controller(WineListCtrl, {$scope: scope});
      $httpBackend.flush();

      spyOn(location, 'path').andCallThrough();
      scope.addWine();
      expect(location.path).wasCalledWith('/wines/new');
    });


    it('should retrieve "wines" from backend call', function() {
      $httpBackend.expectGET('/rest/cellar/wines').respond(wineList());
      controller(WineListCtrl, {$scope: scope});
      $httpBackend.flush();

      expect(scope.wines).toEqualData(wineList());
    });
  });


  describe('WineDetailsCtrl', function() {

    it('should fetch wine detail for given wineId', function() {
      routeParams.wineId = 'xyz';
      $httpBackend.expectGET('/rest/cellar/wines/xyz').respond(wineDetails());
      controller(WineDetailsCtrl, {$scope: scope});

      expect(scope.wine).toEqualData({});
      $httpBackend.flush();

      expect(scope.wine).toEqualData(wineDetails());
    });


    it('should not fetch wine detail for new wine', function() {
      routeParams.wineId = 'new';
      controller(WineDetailsCtrl, {$scope: scope});

      expect(scope.wine).toEqualData({});
      // make sure that no request was triggered
      $httpBackend.verifyNoOutstandingRequest();
    });


    it('should update the parent controller when invoking saveWine with undefined _id', function() {
      routeParams.wineId = 'new';
      controller(WineDetailsCtrl, {$scope: scope});
      expect(scope.wine).toEqualData({});

      $httpBackend.expectPOST('/rest/cellar/wines').respond({'_id': '8888'});
      $httpBackend.expectGET('/rest/cellar/wines').respond(wineList());

      spyOn(location, 'path').andCallThrough();

      scope.saveWine();
      $httpBackend.flush();
      expect(location.path).wasCalledWith('/wines/8888');

      expect(scope.$parent.wines).toEqualData(wineList());
      expect(scope.wine).toEqualData({'_id': '8888'});
    });
 

    it('should not update the parent controller when invoking saveWine with _id', function() {
      var result = wineDetails();
      result['_id'] = 'xyz';

      routeParams.wineId = 'xyz';
      $httpBackend.expectGET('/rest/cellar/wines/xyz').respond(wineDetails());

      controller(WineDetailsCtrl, {$scope: scope});
      $httpBackend.flush();
      scope.wine._id = 'xyz';

      $httpBackend.expectPUT('/rest/cellar/wines/xyz', result).respond();
      $httpBackend.expectGET('/rest/cellar/wines').respond(wineList());

      spyOn(location, 'path');

      scope.saveWine();
      $httpBackend.flush();
      expect(location.path).wasCalledWith('/wines/xyz');

      expect(scope.wine).toEqualData(result);
    });
 

    it('should update the parent controller when invoking deleteWine', function() {
      //var result = wineDetails();
      //result['_id'] = 'xyz';

      routeParams.wineId = 'xyz';
      $httpBackend.expectGET('/rest/cellar/wines/xyz').respond(wineDetails());
      controller(WineDetailsCtrl, {$scope: scope});
      $httpBackend.flush();
      expect(scope.wine).toEqualData(wineDetails());
      scope.wine._id = 'xyz';
      //expect(scope.wine).toEqualData(result);

      $httpBackend.expectDELETE('/rest/cellar/wines/xyz').respond(200, '');
      $httpBackend.expectGET('/rest/cellar/wines').respond(wineList());

      spyOn(scope.wine, '$remove').andCallThrough();
      spyOn(location, 'path').andCallThrough();

      scope.deleteWine();
      $httpBackend.flush();
      expect(location.path).wasCalledWith('/wines');
      expect(scope.wine.$remove).wasCalled();
      expect(scope.$parent.wines).toEqualData(wineList());
    });
  });

});
