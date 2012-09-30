'use strict';

/* jasmine specs for controllers go here */
describe('Testing ajaxdemo controllers', function() {
  var scope, location, ctrl;

  beforeEach(function() {
    // for each testcase initialize a new controller
    scope = {'wines':[]};
    location = {'path':function(apath) {return;}};
    var Wines = {'list': function() {return [{"name":"BLOCK NINE"},{"name":"BODEGA LURTON"}];
    }};
    ctrl = new WineListCtrl(scope, location, Wines);
  });


  it('should change location when calling addWine', function() {
    spyOn(location, 'path');
    scope.addWine();
    expect(location.path).wasCalledWith('/wines/new');
  });


  it('should create "wines" model from backend call', function() {
    expect(scope.wines).toEqual([{"name":"BLOCK NINE"},{"name":"BODEGA LURTON"}]);
  });
});
