import schedule
from processData import doThings
import traceback

doThings()

schedule.every(1).hours.do(doThings)

while True:
	schedule.run_pending()
