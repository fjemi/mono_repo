
# coding: utf-8

# In[ ]:

# r/DailyProgrammer Challenge #2 [hard]
# https://www.reddit.com/r/dailyprogrammer/comments/pjsdx/difficult_challenge_2/
#
# create a stopwatch program. this program should have start, stop, and lap options, 
# and it should write out to a file to be viewed later.


# In[ ]:

#import time
from datetime import datetime, time, timedelta
import math


# In[ ]:

# function that takes in list time (h:m:s) as a string and returns integer for h, m, s
def timeInt(list):
    elapsedtime = 0.00
    hours = 0.00
    minutes = 0.00
    seconds = 0.00
    string = ""
    
    for i in range(0, len(list)):
        string = list[i]
        print (string)
        print (string[0:2], string[3:5], string[6:])
        
        hours = hours + float(string[0:1])
        minutes = minutes + float(string[3:4])
        seconds = seconds + float(string[6:7])
        
    return ()


# In[ ]:

# function that calculates the time (h:m:s) and returns a string

def eTime(time1, time2):
    # 
    elapsedtime = time2.timestamp() - time1.timestamp()
    timeString = " "
    
    # less than 60 seconds
    if (elapsedtime < 60):    
        timestring = ("00:00:%02.0f" % (math.floor(elapsedtime)))
   
    # between 60-3600 seconds
    elif (elapsedtime < 3600):
        minutes = elapsedtime / 60
        seconds = 60 * (minutes - math.floor(minutes))
        timestring = ("00:%02.0f:%02.0f" % (math.floor(minutes), math.floor(seconds)))
    
    # greater than 3600 seconds
    else:
        hours = elapsedtime / 3600
        minutes = (hours - math.floor(hours)) * 60
        seconds = (minutes - math.floor(minutes)) * 60
        timestring = ("%02.0f:%02.0f:%02.0f" % (math.floor(hours), math.floor(minutes), math.floor(seconds)))
    
    
    # return string with the elapsed time
    return timestring


# In[ ]:

def stopWatch():
    startbool = 0 # used to break out of while loops
    splitbool = 0 # used to start/stop splitting
    
    starttime = time(0, 0)
    stoptime = time(0, 0)
    startstop = time(0, 0) # time between the start and stop time
    splittime = time(0, 0)

    # list to hold split times
    laps = []
    
    # used to start time. loops until it gets the desired user input
    while startbool < 1: 
        userinput = input("Enter START to begin" + "\n")
        
        # invalid selection/stopwatch hasn't been started
        if userinput.lower() not in "start":
            print ("Not a valid input! START the clock.")
            continue

        # start the stopwatch
        elif userinput.lower() == "start":
            starttime = datetime.now()
            startbool += 1
        else:
            return 1
    
    # if the stop watch has been started then stop or split it
    if startbool == 1:
        print ("\n" + "Start time - ", starttime)
    
        while startbool != 0:
            userinput = input(("Enter STOP or SPLIT to stop or lap time" + "\n"))
            
            # start or stop the watch once its been started
            if userinput.lower() not in ("stop", "split"):
                print ("Not a valid input! STOP or SPLIT the clock.")
                continue
            
            # stop the startwatch
            elif userinput.lower() == "stop":
                stoptime = datetime.now()
                startbool = 0
                print ("Stop time - ", stoptime)
                print ("Elapsed Time (h:m:s) -", eTime(starttime, stoptime))
            
            # split stopwatch FUNCTION DOESN'T WORK
            else: #userinput.lower() == "split":
                splitbool = 1
                splittime = datetime.now()
                laps.append(eTime(starttime, splittime))
                
                # keeps splitting/looping until stop
                while splitbool != 0:
                    userinput = input(("Enter SPLIT or STOP" + "\n"))
                    
                    if userinput.lower() not in ("stop", "split"):
                        print ("Not a valid input! STOP or SPLIT the clock.")
                        continue
                    
                    elif (userinput.lower() == "split"):
                        starttime = datetime.now()
                        
                        if (splitbool % 2 != 0):
                            splittime = datetime.now()
                            laps.append(eTime(starttime, splittime))
                        else:
                            starttime = datetime.now()
                        continue
                            
                        splitbool += 1
                    
                    # if stop and time isn't running do nothing
                    elif (userinput.lower() == "stop" and splitbool % 2 != 0):
                        for i in range(0, len(laps)):
                            print ("Lap %s (h:m:s) - %s" % (i + 1, laps[i]))
                            timeInt(laps)
                        break
                    
                    # split and start has to be true stop after splitting
                    else: 
                        splittime = datetime.now()
                        splitbool = 0
                        laps.append(eTime(starttime, splittime))
                        for i in range(0, len(laps)):
                            print ("Lap %s (h:m:s) - %s" % (i + 1, laps[i]))
                        
                        # test timeInt function
                        timeInt(laps)
                        break
                break


# In[ ]:

# run the stopwatch
stopWatch()

