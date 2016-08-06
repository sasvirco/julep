#!/usr/bin/python
import json
import logging
import sys
import argparse
import yaml
import time
import hpoo as oo
from junit_xml import TestSuite, TestCase

def main () :

	levels = {
		'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL
	}
	

	parser = argparse.ArgumentParser(description = 'HP Operation Orchestration testing tool')
	parser.add_argument('--configfile', default = 'julep.yaml', help='Configfile with hpoo flow testcases')
	parser.add_argument('--loglevel', default = 'INFO', help='FATAL, ERROR, WARNING, INFO, DEBUG')
	parser.add_argument('--logfile', default = 'julep.log', help='Logfile to store messages (Default: julep.log)')
	parser.add_argument('--timeout', default = 3600, type = int, help='The time to wait for flow completion in seconds (Default: 3600 - 1hour)')
	parser.add_argument('--heartbeat', default = 120, type = int, help='Operation Orchestration polling interval (Default: 120 secs)')
	parser.add_argument('--quiet', action='store_true', help='Do not print logging to stdout')
	parser.add_argument('--trustcert', action='store_true', help='Trust self-signed certs')
	parser.add_argument('--configfmt', default = 'yaml', help="Configfile format - json or yaml. Default json.")
	parser.add_argument('--delay', default = 15, type = int, help="Delay in seconds to wait between starting flows")
	parser.add_argument('--junitoutput', default = 'julepout.xml', help="Delay in seconds to wait between starting flows")

	args = parser.parse_args()
	loglevel = levels.get(args.loglevel, logging.NOTSET)
	logging.basicConfig(
		level= args.loglevel,
		format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
		datefmt='%m-%d %H:%M',
		filename= args.logfile,
		filemode='a')

	root = logging.getLogger()

	if args.quiet is False: 
		console = logging.StreamHandler()
		console.setLevel(args.loglevel)
		
		formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
		console.setFormatter(formatter)
		
		root.addHandler(console)

	logging.info("Want some blacksea julep?")
	config = parse_config(args.configfile, args.configfmt)
	config['general']['trustcert'] = args.trustcert

	testcases = {
		'running' : [],
		'finished' : [],
	}

	for flow in config['flows'] :
		test = oo.hpoo(config['general'], flow)
		name = test.run()
		if args.delay is not None:
			logging.info("sleeping between runs for %s secs", args.delay)
			time.sleep(args.delay)
		testcases['running'].append(test)

	root.debug(testcases)

	timeout = int(args.timeout)
	heartbeat = int(args.heartbeat)
    
	while timeout >= heartbeat :
		logging.info('Tracking testcases in running state')
		for test in testcases['running'] :
			
			if test.get_status() == 'RUNNING' :
				continue
			else :	
				testcases['finished'].append(test)
				testcases['running'].remove(test)

			logging.debug(testcases)

		if len(testcases['running']) == 0 :
			root.info("Running testcases list is zero, we are done")
			break

		logging.info('Waiting %s seconds for next heartbeat', str(heartbeat))
		timeout = timeout - heartbeat
		time.sleep(heartbeat)
	
	testresults = []
	logging.info("Generating junit xml output")	

	for test in testcases['finished'] :
		result = test.collect()
		flow = test.get_flow()
		testname = flow['name'] + " " + test.get_run_id()

		logging.info("Asserts for "+flow['name'])
		errors = []

		for k,v in flow['assert'].items() :
			 if all(item in result[k].items() for item in flow['assert'][k].items()) is False:
				errors.append("Failed to assert "+k)		
		
		if errors :
			tc = TestCase(testname,flow['uuid'],'',errors)
			tc.add_failure_info(errors)
			logging.info("Adding failed test")
			testresults.append(tc)
		else :
			logging.info("Adding succesfull test")
			duration = int(result['executionSummary']['endTime'] - result['executionSummary']['startTime'])
			tc = TestCase(testname,flow['uuid'],duration/1000.0,result['executionSummary']['resultStatusType'],'')
			testresults.append(tc)

	
	ts = TestSuite('ootests', testresults)
	with open(args.junitoutput, 'w') as f:
		TestSuite.to_file(f, [ts], prettyprint=True)
		logging.info("Writing output to "+args.junitoutput)
	

def parse_config(configfile, fmt) :
	f = open(configfile,'r')
	txt = f.read()
	logging.debug(txt)

	if fmt == "json" :
		return json.loads(txt)

	return yaml.load(txt)


if __name__ == "__main__":
	main()
