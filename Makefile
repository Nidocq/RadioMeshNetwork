
run: proj.py
		/opt/homebrew/bin/python3 proj.py

test: proj.py
	python3 -m unittest Tests/tests.py
