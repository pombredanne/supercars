Supercars Javascript application
================================

Supercars application implemented using AngularJS

It is based on the AngularJS skeleton (https://github.com/angular/angular-seed).

I had to exchange the PHP backend to a Python/mongodb one.

Another important thing I had to add is testing.


Acknowledgements
================

I started the Supercars application based on a skeleton taken from here:
http://coenraets.org/blog/2012/02/sample-application-with-angular-js/

The supercar images are creative commons license mostly from wikipedia. Please refer to the included IMAGE_LICENSES file for details.

Many thanks to cristatus from the Angularjs IRC channel. He helped me out debugging the supercars sample app.


Debugging in Developer Tools
============================

Select an element and type the following into the console "angular.element($0).scope()".


Restful Service
===============

For demonstration I wrote a small RESTful service based on SimpleHTTPServer. This server is used to both serve the restful webservice and the application itself in order to comply with the same origin policy of the browsers.


Interface for a restful webservice
----------------------------------

To create a resource on the server, use POST.
To retrieve a resource, use GET.
To change the state of a resource or to update it, use PUT.
To remove or delete a resource, use DELETE.

This means using the HTTP protocol as it is intended.


Installing demo and tools
-------------------------

All you need is a Python installation.


Working on Jasmine-Unit-Tests
-----------------------------

The ajaxdemo sample uses Testacular for Javascript unit testing. We assume that you have a Node.js installation on your machine and the testacular package installed as well.

Testacular comes with a watcher which runs the Jasmine unittests every time you change a file. You can start the watcher with this command:

./script/test.sh


Run the Supercars application
-----------------------------

python ./scripts/restserver.py


Visit the Supercars app
-----------------------

Just point your browser to:
http://localhost:8000/index.html
