import numpy as np
import scipy
import os
from sklearn.metrics.pairwise import cosine_similarity

debug=0

def readfile(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    d = {}
    for l in lines:
        elems = l.split(',')
        d[elems[0].strip()] = map(float, np.array(elems[1:]))
    return d

def setInterval(d, interval):
    for k in d:
        res = []
        i = 0
        while i < len(d[k]):
            res.append(0)
            for j in range(i, min(i + interval, len(d[k]))):
                if d[k][j] == 1:
                    res[len(res) - 1] =  1
                    break
            i = i + interval
        d[k] = res


def getIntervals(device_min_visibility, interval, wemo):
    device_interval_visibility = {}
    for device in device_min_visibility:
        device_interval_visibility[device] = []
        total_mins = len(device_min_visibility[device])
        for current_interval in range(0, total_mins/interval):
            visible = 0
            for min_within_interval in range(0, interval):
                curr_min = current_interval*interval+min_within_interval
                visible = visible | int(device_min_visibility[device][curr_min])
                if debug:
                    print device + " min:" + str(curr_min) + " visible:" + str(visible)
            # device visiblity during in the interval
            if debug:
                print device + " interval:" + str(current_interval) + " visible" + str(visible)
            device_interval_visibility[device].append(visible)
            
    return device_interval_visibility

            
def findTransitionPointsForDevice(device_name, min_intervals_for_transition, device_interval_visibility):        
    device_visibility_array = device_interval_visibility[device_name]
    transition_intervals = [] 
    for interval in range(0,len(device_visibility_array)):
        # check left values
        is_transition_point = True
        for prev_interval in range( interval - min_intervals_for_transition, interval):
            if prev_interval >= 0:
                if device_visibility_array[interval] == device_visibility_array[prev_interval]:
                    is_transition_point = False
                    break
            else:
                is_transition_point = False
                break
        
        # check 
        if is_transition_point == True:
            transition_intervals.append(interval)
            if debug:
                print "Transition point:" + device_name + ":" + " interval:" + str(interval) +  str(device_interval_visibility[device_name][interval-min_intervals_for_transition:interval+1])
        else:
            if debug:
                print "Not Transition point:" + device_name + ":" + " interval:" + str(interval)
    return transition_intervals
    

def OLDgetIntervals(d, interval, wemo):
    for w in wemo:
        for i in range(0, len(d) - 1):
            if d[w][i] != d[w][i + 1]:
                    start_interval = max(0, i - interval)
                    end_interval = min(len(d), i + interval)
                    print("intervals/" + str(w) + "_" + str(i)+ ".txt")
                    f = open( "intervals/" + str(w) + "_" + str(i)+ ".txt", 'w')
                    f.write(str(w) + " " + str(d[w][start_interval : end_interval]) + "\n")
                    for device in d:
                        if device != w:
                            f.write(str(device) + " " + str(d[device][start_interval : end_interval]) + "\n")
                    f.close()
                

    
                
def OLDwriteCosine(filename, dictionary, wemo):
    f = open(filename, "w")
    arr = []
    for w in wemo:
        for device in dictionary:
            if device != w:
                sim = cosine_similarity(dictionary[w], dictionary[device])[0][0]
                arr.append((sim, str(w) + " " + str(device) + " : " + str(sim) + "\n"))
    arr.sort(reverse=True, key=lambda x : x[0])    
    for e in arr:
        f.write(e[1])
    

def writeCosine(filename, dictionary, wemo):
    arr = []
    for w in wemo:
        for device in dictionary:
            if device != w:
                sim = cosine_similarity(dictionary[w], dictionary[device])[0][0]
                arr.append((sim, str(w) + " " + str(device) + " : " + str(sim) + "\n"))
    arr.sort(reverse=True, key=lambda x : x[0])    
    return arr

device_visibility_by_minute = readfile("/tmp/dec2829.txt")
#setInterval(device_visibility_by_minute, 1)
interval=15
device_interval_visibility=getIntervals(device_visibility_by_minute, interval,["tejlightWeMo%20Insight", "sunlightWeMo%20Switch1"])

print "Device Visibility interval:" + str(interval)
for device in device_interval_visibility:
    print str(device) + ":" + str(device_interval_visibility[device])

device_name = "tejlightWeMo%20Insight"
min_intervals_for_transition = 2
transition_intervals = findTransitionPointsForDevice(device_name, 
                                                     2, #min_intervals_for_transition, 
                                                     device_interval_visibility)

print "Transition points:" + device_name
print transition_intervals

for transition_interval in transition_intervals:
    device_visibility_near_transition = {}
    for device in device_interval_visibility:
        device_visibility_near_transition[device] = []
        for  curr_interval in range(transition_interval-min_intervals_for_transition, transition_interval+min_intervals_for_transition):
            if (curr_interval < 0 or   curr_interval > len(device_interval_visibility[device])) :
                pass
            else:
                device_visibility_near_transition[device].append(device_interval_visibility[device][curr_interval])
    # apply algo on the intervals near transition point 
    
    device_cosine_similarity = writeCosine(device_name + "_cosine_similarity.txt", device_visibility_near_transition, [device_name])
    print "============= Cosine similariy:" + device_name + " for transition interval" + str(transition_interval)
    print "Input:"
    for device in device_visibility_near_transition:
        print " " + device + ":" + str(device_visibility_near_transition[device])

    # print device_cosine_similarity
    print "Result:"
    for entry in device_cosine_similarity:
        print " " + str(entry)
        
        
    

#writeCosine("cosine_similarity.txt", device_visibility_by_minute, ["tejlightWeMo%20Insight", "sunlightWeMo%20Switch1"])
            
    
