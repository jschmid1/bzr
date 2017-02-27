.PHONY: test 
.PHONY: server
test:   
	tox
dev: 
	sh setup.sh
	export DB_ENV=development;python seed.py
	export DB_ENV=development;python server.py

production:
	export DB_ENV=production;python server.py

all: test dev

