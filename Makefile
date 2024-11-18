


all: proj.py
		/opt/homebrew/bin/python3 scenarios/4asrow.py

test: proj.py
	python3 -m unittest Tests/tests.py

scenario: proj.py
	python3 -i scenarios/createScenario.py 5 65040 65090 6 25 5 0

