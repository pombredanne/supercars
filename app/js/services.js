'use strict';

/* Services */

// angular.module('cellar.services', []).
//   value('version', '0.1');


angular.module('cellar.services', ['ngResource']).
    factory('Wine', function($resource) {
        return $resource('cellar/:wineId.json', {}, {
            query: {method: 'GET', params:{wineId:'wine'}, isArray:false}
        });
    });


/*



angular.module('phonecatServices', ['ngResource']).
    factory('Phone', function($resource){
  return $resource('phones/:phoneId.json', {}, {
    query: {method:'GET', params:{phoneId:'phones'}, isArray:true}
  });
});


/* 
angular.module('cellar.services', ['ngResource']).
    factory('Wine', function($resource) {
        return $resource('http://localhost:27080/cellar/wines/_find?criteria=%7B%22_id%22%3A%7B%22%24oid%22%3A%224fb784bcb0ab582e8e000000%22%7D%7D', {}, {
            get: {method: 'GET', params:{}, isArray:false}
        });
    });

angular.module('phonecatServices', ['ngResource']).
    factory('Phone', function($resource){
  return $resource('phones/:phoneId.json', {}, {
    query: {method:'GET', params:{phoneId:'phones'}, isArray:true}
  });
});
*/