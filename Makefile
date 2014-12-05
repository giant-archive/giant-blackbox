all: run

setup:
	virtualenv ./env
	./env/bin/pip install -r ./etc/requirements.txt

run: 
	./env/bin/nosetests ./src --with-xunit --xunit-file=./nosetests.xml