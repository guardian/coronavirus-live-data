import schedule
from test import test
from datetime import datetime
from processData import runScripts

runScripts()

schedule.every(1).hours.do(runScripts)

while True:
	schedule.run_pending()