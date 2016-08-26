# Julep

Julep is a simple testing framework for HP Operation Orchestration. It produces JUnit compatible test results which makes it very convinient to integrate with Jenkins.


# Usage
```
usage: julep.py [-h] [--configfile CONFIGFILE] [--loglevel LOGLEVEL]
                [--logfile LOGFILE] [--timeout TIMEOUT]
                [--heartbeat HEARTBEAT] [--quiet] [--trustcert]
                [--configfmt CONFIGFMT] [--delay DELAY]
                [--junitoutput JUNITOUTPUT]

HP Operation Orchestration testing tool

optional arguments:
  -h, --help            show this help message and exit
  --configfile CONFIGFILE
                        Configfile with hpoo flow testcases
  --loglevel LOGLEVEL   FATAL, ERROR, WARNING, INFO, DEBUG
  --logfile LOGFILE     Logfile to store messages (Default: julep.log)
  --timeout TIMEOUT     The time to wait for flow completion in seconds
                        (Default: 3600 - 1hour)
  --heartbeat HEARTBEAT
                        Operation Orchestration polling interval (Default: 120
                        secs)
  --quiet               Do not print logging to stdout
  --trustcert           Trust self-signed certs
  --configfmt CONFIGFMT
                        Configfile format - json or yaml. Default json.
  --delay DELAY         Delay in seconds to wait between starting flows
  --junitoutput JUNITOUTPUT
                        Delay in seconds to wait between starting flows

```

- quiet - By default Julep prints detailed logs in both logfile and console. The quiet option will suppress stdout messages.
- junitoutput - the location of the junit xml file that contains the test cases results
- delay - that option is used to not flood hpoo with numerous api calls. It introduces  delay betwen the api calls. Defaults to 15 seconds.
- heartbeat - when flows are running, Julep will wait for them to finish. The heartbeat defines on what intervals it checks for status. Defaults to 120 seconds.
- timeout - How long to give a test before it produces results. Defaults to 3600 seconds(1h).
- trustcert - trust the ssl certificates, usefull with self-signed ones
- loglevel - defines the verbosity of the logs. Info provides information about what is currently going on, while DEBUG prints very detailed requests and reponses, very usefull with identifying issues.

#Config file
The configfile can be either in json or yaml format. It includes 2 objects. General, where the url for the hpoo service and credentials are defined, and the flows, that contains an array of objects where information about the tests we want to make resides.

###Example in yaml
```yaml
---
  general: 
    username: "admin"
    password: "secret"
    url: "https://localhost:8443/oo"
  flows: 
    - 
      uuid: "64cdf48b-54ec-4704-a6ad-2ec85c74cecf"
      name : "Testing if flow will fail"
      inputs: 
        fail: "true"
        req: "asdf"
      assert: 
        flowOutput: 
          var1: "var1"
          var2: "var2"
        executionSummary: 
          resultStatusType: "ERROR"
    - 
      uuid: "64cdf48b-54ec-4704-a6ad-2ec85c74cecf"
      name : "Testing if flow will succeed "
      inputs: 
        fail: "false"
        req: "asdf"
      assert: 
        flowOutput: 
          var1: "var1"
          var2: "var2"
        executionSummary: 
          resultStatusType: "RESOLVED"
    - 
      uuid: "64cdf48b-54ec-4704-a6ad-2ec85c74cecf"
      name : "Testing other features"
      inputs: 
        fail: "false"
        req: "asdf"
      assert: 
        flowOutput: 
          var1: "var1"
          var2: "var2"
        executionSummary: 
          resultStatusType: "RESOLVED"
    - 
      uuid: "64cdf48b-54ec-4704-a6ad-2ec85c74cecf"
      name : "Testing result statuses"
      inputs: 
        fail: "false"
        req: "asdf"
      assert: 
        flowOutput: 
          var1: "var1"
          var2: "var2"
        executionSummary: 
          resultStatusType: "RESOLVED"
```

#Configuration options
##General 
- url - the url for the hpoo server
- username - the username to connect with
- password - the password

## Flows 
- uuid  - The UUID of the flow that we want to test
- name  - A meaningful name for our test (e.g "Deploy chef client via ssh")
- inputs - The inputs with which we want to run the flow. Take into consideration, that all mandatory inputs will have to be supplied.
- assert - Assert contains an object that has the same keys and values as the output returned by the execution log. Julep will assert the result with your expected vaulues and fail the test if they do not match. So far the most used ones are flowOutput, that contains the returned by the flow results and the resultStatusType from the executionSummary object, that contains RESOLVED or ERROR depending whether the flow failed or succeeded.

### Example JUnit output
```xml
<?xml version="1.0" ?>
<testsuites errors="0" failures="0" tests="3" time="0.454">
	<testsuite errors="0" failures="0" name="ootests" skipped="0" tests="3" time="0.454">
		<testcase classname="64cdf48b-54ec-4704-a6ad-2ec85c74cecf" name="Testing if flow will fail 174201531" time="0.194000">
			<system-out>ERROR</system-out>
		</testcase>
		<testcase classname="64cdf48b-54ec-4704-a6ad-2ec85c74cecf" name="Testing if flow will succeed 2 174201551" time="0.129000">
			<system-out>RESOLVED</system-out>
		</testcase>
		<testcase classname="64cdf48b-54ec-4704-a6ad-2ec85c74cecf" name="Testing if flow will succeed  174201541" time="0.131000">
			<system-out>RESOLVED</system-out>
		</testcase>
	</testsuite>
```
