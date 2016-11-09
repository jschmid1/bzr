.PHONY: test 
.PHONY: server
test:   
	export DB_ENV=testing;behave -D BEHAVE_DEBUG_ON_ERROR=yes api/tests/features

server: 
	export DB_ENV=development;python server.py
	export DB_ENV=development;python server.py

production:
	export DB_ENV=production;python server.py

all: test server
