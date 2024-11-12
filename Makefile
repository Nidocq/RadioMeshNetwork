


all: proj.py
		/opt/homebrew/bin/python3 scenarios/4asrow.py

test: proj.py
	python3 -m unittest Tests/tests.py
