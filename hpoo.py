import logging
import json
import sys
import requests
import requests.packages.urllib3
import time
from base64 import encodestring

class hpoo():

	def __init__(self, config = None, flow = None):

		self.config = config
		self.flow = flow

		self.session = requests.Session()
		self.session.url = self.config['url']
		self.auth = encodestring(self.config['username']+ ":" + self.config['password'])
		self.session.headers.update({'Authorization': 'Basic '+ self.auth.rstrip()})
		self.session.headers.update({'Accept':'application/json'})

		self.error = None
		self.run_id = None
		self.status = None
		self.flow_result = None

		if self.config['trustcert'] is True :
			requests.packages.urllib3.disable_warnings() 

	def run(self) :
		logging.info('Entering run_flow')

		#collect flow information
		url = self.session.url +'/rest/v1/flows/'+ self.flow['uuid']
		r = self.session.get(url, verify=False)

		if (r.reason != 'OK') :
			raise Exception(r.reason)

		logging.debug(r.text)
		flow_info = json.loads(r.text)
	
		#check mandatory flow inputs
		url = self.session.url + '/rest/v1/flows/' + self.flow['uuid'] + '/inputs'
		r = self.session.get(url,verify=False)

		if (r.reason != 'OK') :
			raise Exception (r.reason)

		logging.debug(r.text)

		if (r.text) :
			flow_input = json.loads(r.text)

		for i in flow_input:
			if (i['mandatory'] is True and i['name'] not in self.flow['inputs']) :
				raise Exception('Missing required flow input: ' + i['name'])
	
		#construct json post object
		post_data = {}
		post_data['uuid'] = self.flow['uuid']
		post_data['runName'] = flow_info['name']
		post_data['logLevel'] = 'DEBUG'
		
		if (input is not None) :
			post_data['inputs']	 = self.flow['inputs']

		json_post = json.dumps(post_data)

		#run the flow
		url = self.session.url + '/rest/v1/executions'
		self.session.headers = {'Content-type':'application/json'}
		r = self.session.post(url, data=json_post, verify=False)
	
		if (r.reason != 'Created') :
			logging.debug(r.reason)
			raise Exception (r.reason)
		else :
			response  = json.loads(r.text)
			logging.debug(response)
			self.run_id = response['executionId']
			return response['executionId']	

	def get_status(self) :

		logging.info('Getting execution summary')

		url = self.session.url + '/rest/v1/executions/' + self.run_id + '/summary'

		r = self.session.get(url, verify=False)
		if (r.reason != 'OK'):
			raise Exception(r.reason)
	
		logging.debug(r.text)
		response = json.loads(r.text)

		return response[0]['resultStatusType']

	def collect(self) :

		logging.info('Entering collect_result')

		url = self.config['url'] + '/rest/v1/executions/' + self.run_id + '/execution-log'

		r = self.session.get(url, verify=False)
		if (r.reason != 'OK') :
			raise Exception(r.reason)

		logging.debug(r.text)
		result = json.loads(r.text)
		self.flow_result = result
		
		return result
	
	def get_run_id(self) :
		return self.run_id

	def get_error(self) :
		return self.error

	def get_status(self) :
		return self.status

	def get_flow_result(self) :
		return self.flow_result

	def get_flow(self) :
		return self.flow
