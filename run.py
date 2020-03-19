import scheduleß
from processData import runScripts

runScripts()

schedule.every(1).hours.do(runScripts)

while True:
	schedule.run_pending()