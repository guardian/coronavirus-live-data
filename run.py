import schedule
from processData import doThings
import traceback

doThings()

schedule.every(30).seconds.do(doThings)

while True:
	schedule.run_pending()
