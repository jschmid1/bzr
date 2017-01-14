# Bzr 

[![Build Status](https://travis-ci.org/jschmid1/bzr.svg?branch=master)](https://travis-ci.org/jschmid1/bzr)

Disclaimer: 

That project is mainly for learning purposes.


### What is Bzr --> Bazaar

Trying to mimic the real world market - supply and demand -  in a very small factor.
Selling/Buying goods and eventually producing commodities to gain wealth.

### Technologies

- Docker:

All components of this application will run as microservices that can be containerized.

- Cpp(or Haskell):

Continiously tracks the fluctuation of goods and adjusts the prices to feed the updated values back to the database.

- Database:

Postgresql - Rather simple schema.

Users - BasicGoods - Producables - Producables-BasicGoods

- REST API

All data will be exposed/consumed via a REST-API that gets its data from the Database

- Various clients

Android, commandline(preferably in rust), GUI(QT), Web(ReactJS/AngularJS)

- Simulation

Simulating a large playerbase to find disparities.


------------

### Testing

Every component will be covered with speparate tests and piped into a continuous integration system.



### Setup

-----------

create a virtualenv

`virtualenv --python=3.4 api/venv`

source the venv:

`source api/venv/bin/activate`

Setup a development environment:

`make dev`

Run tests

`make test`

Setup a production environment:

`make production`
