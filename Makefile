bamboo:
	virtualenv ./env
	./env/bin/pip install -r ./etc/requirements.txt
	./env/bin/nosetests ./src --with-xunit --xunit-file=./nosetests.xml