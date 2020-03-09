#!/usr/local/bin/python3
import matplotlib.pyplot as plt
import random
import sys

data = sys.stdin.readlines()

savedStartTime = [None] * 10000;

mintime = 15767005040;
maxtime = 0;
for i in data:	
	el = i.split("|");
	command = el[0];
	if (command == "REQSTART"):
		if mintime > float(el[1]): 
			mintime = float(el[1]);
		if maxtime < float(el[1]): 
			maxtime = float(el[1]);	
averageStartTime = 0;
averageEndTime = 0;
cnt = 0;
sumStartTime = 0;
sumEndTime = 0
cntEnd = 0;

for i in data:	
	el = i.split("|");
	command = el[0];
	if (command == "REQSTART"):
		starttime = float(el[1]) - mintime;
		num = int(el[2]);
		savedStartTime[num] = starttime;
		plt.hlines(num, starttime, maxtime-mintime, colors='yellow')
		cnt =cnt + 1;

	if (command == "REQEND"):
		num = int(el[2]);
		starttime = savedStartTime[num];
		endtime = float(el[3]) + starttime;
		status = el[4];
		res = el[5];
		color = "black";
		if status != "200":
		 	color = "red" 
		print ("plt.hlines(num, "+str(starttime)+", "+str(endtime)+", colors=color)");
		plt.hlines(num, starttime, endtime, colors=color)

		sumStartTime = sumStartTime + starttime;
		sumEndTime = sumEndTime + endtime;
		cntEnd = cntEnd + 1;				


#for x in range(mintime, maxtime, 1):
#    color = random.choice(['red', 'green', 'blue', 'yellow'])
#    plt.hlines(1, x, x + 2, colors=color, lw=5)
#    plt.text(x + 1, 1.01, color, ha='center')

averageEndTime = sumEndTime / cntEnd;
averageStartTime = sumStartTime / cntEnd;

#plt.vlines(averageEndTime, 0, cnt, colors='red', linestyles='dashed')
#plt.vlines(averageStartTime, 0, cnt, colors='blue', linestyles='dashed')
plt.title(str(cnt) + " requests to hybris ");

plt.ylabel('requests')
plt.xlabel('time (s)')


plt.show()
