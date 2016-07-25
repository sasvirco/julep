#!/usr/bin/python
import json
import logging
import sys
import argparse
import requests
import requests.packages.urllib3
import yaml
import time
import hpoo as oo
from base64 import encodestring

def main () :

	levels = {
		'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL
	}
	

	parser = argparse.ArgumentParser(description = 'Run HP OO 10 flow from the command line')
	parser.add_argument('--configfile', default = 'julep.yaml', help='Configfile with hpoo flow testcases')
	parser.add_argument('--loglevel', default = 'DEBUG', help='FATAL, ERROR, WARNING, INFO, DEBUG')
	parser.add_argument('--logfile', default = 'julep.log', help='Logfile to store messages (Default: julep.log)')
	parser.add_argument('--timeout', default = 3600, type = int, help='The time to wait for flow completion in seconds (Default: 3600 - 1hour)')
	parser.add_argument('--heartbeat', default = 120, type = int, help='Operation Orchestration polling interval (Default: 120 secs)')
	parser.add_argument('--quiet', action='store_true', help='Do not print logging to stdout')
	parser.add_argument('--trustcert', action='store_true', help='Trust self-signed certs')
	parser.add_argument('--configfmt', default = 'yaml', help="Configfile format - json or yaml. Default json.")
	parser.add_argument('--delay', default = 15, help="Delay in seconds to wait between starting flows")

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

	logging.info("want some julep?")
	cfg = parse_config(args.configfile, args.configfmt)
	cfg['general']['trustcert'] = args.trustcert

	testcases = {
		'running' : [],
		'finished' : [],
	}

	for flow in cfg['flows'] :
		test = oo.hpoo(cfg['general'], flow)
		test.run()
		if args.delay is not None:
			logging.info("sleeping between runs for %s secs", args.delay)
			time.sleep(args.delay)
		testcases['running'].append(test)

	root.debug(testcases)

	timeout = int(args.timeout)
	heartbeat = int(args.heartbeat)
    
	while timeout >= heartbeat :
		logging.info('Checking remaining flows')
		for test in testcases['running'] :
			
			if test.get_status() == 'RUNNING' :
				continue
			else :	
				testcases['finished'].append(test)
				testcases['running'].remove(test)

			logging.debug(testcases)

		if len(testcases['running']) == 0 :
			root.info("Running testcases list is zero")
			break

		logging.info('sleeping for %s seconds', str(heartbeat))
		timeout = timeout - heartbeat
		time.sleep(heartbeat)
	

	


def parse_config(configfile, fmt) :
	f = open(configfile,'r')
	txt = f.read()
	logging.debug(txt)

	if fmt == "json" :
		return json.loads(txt)

	return yaml.load(txt)


if __name__ == "__main__":
	main()
