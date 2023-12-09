test: test-sample-input

test-sample-input:
	@cat test/sample_input_data.txt | ./bin/aircontrol.py
