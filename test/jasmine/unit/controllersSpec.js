'use strict';

/* jasmine specs for controllers go here */
describe('ajaxdemo controllers', function() {
  var scope, location, routeParams, $httpBackend, controller;
  var supercarDetails = function() {
      return {
          "name":"AC Cobra",
          "country":"United States",
          "top_speed":"160",
          "power":"485"
      };
  };
  var supercarList = function() {
    return [{"name":"AC Cobra"},{"name":"Aston Martin DB9"}];
  };

  beforeEach(function(){
    this.addMatchers({
      toEqualData: function(expected) {
        return angular.equals(this.actual, expected);
      }
    });
  });

  beforeEach(module('supercars.services'));

  beforeEach(inject(function(_$httpBackend_, $rootScope, $location, 
      $routeParams, $controller) {
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


  describe('SupercarListCtrl', function() {

    it('should change location when calling addSupercar', function() {
      $httpBackend.expectGET('/rest/supercars').respond(supercarList());
      controller(SupercarListCtrl, {$scope: scope});
      $httpBackend.flush();

      spyOn(location, 'path').andCallThrough();
      scope.addSupercar();
      expect(location.path).wasCalledWith('/supercars/new');
    });


    it('should retrieve "supercars" from backend call', function() {
      $httpBackend.expectGET('/rest/supercars').respond(supercarList());
      controller(SupercarListCtrl, {$scope: scope});
      $httpBackend.flush();

      expect(scope.supercars).toEqualData(supercarList());
    });
  });


  describe('SupercarDetailsCtrl', function() {

    it('should fetch supercar detail for given supercarId', function() {
      routeParams.supercarId = 'xyz';
      $httpBackend.expectGET('/rest/supercars/xyz').respond(supercarDetails());
      controller(SupercarDetailsCtrl, {$scope: scope});

      expect(scope.supercar).toEqualData({});
      $httpBackend.flush();

      expect(scope.supercar).toEqualData(supercarDetails());
    });


    it('should not fetch supercar detail for new supercar', function() {
      routeParams.supercarId = 'new';
      controller(SupercarDetailsCtrl, {$scope: scope});

      expect(scope.supercar).toEqualData({});
      // make sure that no request was triggered
      $httpBackend.verifyNoOutstandingRequest();
    });


    it('should update the parent controller when invoking saveSupercar with undefined _id', function() {
      routeParams.supercarId = 'new';
      controller(SupercarDetailsCtrl, {$scope: scope});
      expect(scope.supercar).toEqualData({});

      $httpBackend.expectPOST('/rest/supercars').respond({'_id': '8888'});
      $httpBackend.expectGET('/rest/supercars').respond(supercarList());

      spyOn(location, 'path').andCallThrough();

      scope.saveSupercar();
      $httpBackend.flush();
      expect(location.path).wasCalledWith('/supercars/8888');

      expect(scope.$parent.supercars).toEqualData(supercarList());
      expect(scope.supercar).toEqualData({'_id': '8888'});
    });
 

    it('should not update the parent controller when invoking saveSupercar with _id', function() {
      var result = supercarDetails();
      result['_id'] = 'xyz';

      routeParams.supercarId = 'xyz';
      $httpBackend.expectGET('/rest/supercars/xyz').respond(supercarDetails());

      controller(SupercarDetailsCtrl, {$scope: scope});
      $httpBackend.flush();
      scope.supercar._id = 'xyz';

      $httpBackend.expectPUT('/rest/supercars/xyz', result).respond();
      $httpBackend.expectGET('/rest/supercars').respond(supercarList());

      spyOn(location, 'path');

      scope.saveSupercar();
      $httpBackend.flush();
      expect(location.path).wasCalledWith('/supercars/xyz');

      expect(scope.supercar).toEqualData(result);
    });
 

    it('should update the parent controller when invoking deleteSupercar', function() {
      //var result = supercarDetails();
      //result['_id'] = 'xyz';

      routeParams.supercarId = 'xyz';
      $httpBackend.expectGET('/rest/supercars/xyz').respond(supercarDetails());
      controller(SupercarDetailsCtrl, {$scope: scope});
      $httpBackend.flush();
      expect(scope.supercar).toEqualData(supercarDetails());
      scope.supercar._id = 'xyz';
      //expect(scope.supercar).toEqualData(result);

      $httpBackend.expectDELETE('/rest/supercars/xyz').respond(200, '');
      $httpBackend.expectGET('/rest/supercars').respond(supercarList());

      spyOn(scope.supercar, '$remove').andCallThrough();
      spyOn(location, 'path').andCallThrough();

      scope.deleteSupercar();
      $httpBackend.flush();
      expect(location.path).wasCalledWith('/supercars');
      expect(scope.supercar.$remove).wasCalled();
      expect(scope.$parent.supercars).toEqualData(supercarList());
    });
  });

});
