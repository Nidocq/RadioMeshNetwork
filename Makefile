


all: meshNetwork.py
		/opt/homebrew/bin/python3 scenarios/4asrow.py

test: meshNetwork.py
	python3 -m unittest Tests/tests.py

scenario: meshNetwork.py
	python3 -i scenarios/createScenario.py 5 65040 65090 6 25 5 0 0 50

string5:
	python3 -i scenarios/ninrow.py 5

string20:
	python3 -i scenarios/ninrow.py 20
