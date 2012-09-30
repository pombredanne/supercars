'use strict';

/* jasmine specs for services go here */
describe('Testing ajaxdemo services', function() {
    var service, $httpBackend;

    beforeEach(function(){
        this.addMatchers({
            toEqualData: function(expected) {
                return angular.equals(this.actual, expected);
            }
        });
    });
    beforeEach(module('cellar.services'));
    beforeEach(inject(function(Wine, _$httpBackend_) {
        service = Wine;
        $httpBackend = _$httpBackend_;
    }));

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });


    it('should invoke service without any parameters for list', function() {
        var wine_list = [
            {"name":"BLOCK NINE","year":"2009","grapes":"Pinot Noir","country":"USA","region":"California","description":"With hints of ginger and spice, this wine makes an excellent complement to light appetizer and dessert fare for a holiday gathering."},
            {"name":"BODEGA LURTON","year":"2011","grapes":"Pinot Gris","country":"Argentina","region":"Mendoza","description":"Solid notes of black currant blended with a light citrus make this wine an easy pour for varied palates."}];
        $httpBackend.whenGET('/rest/cellar/wines').respond(wine_list);

        $httpBackend.expectGET('/rest/cellar/wines');

        var res = service.list();
        $httpBackend.flush();
        expect(res).toEqualData(wine_list);
    });

});
