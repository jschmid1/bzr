.PHONY: test 
.PHONY: server
.PHONY: compileC
test:   
	export DB_ENV=testing;behave -D BEHAVE_DEBUG_ON_ERROR=yes api/tests/features

dev: 
	sh setup.sh
	export DB_ENV=development;python seed.py
	export DB_ENV=development;python server.py
	export DB_ENV=development;python process_buildqueue.py


production:
	export DB_ENV=production;python server.py

all: test dev
