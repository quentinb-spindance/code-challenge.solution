""" Python solution attempt for the SpinDance Code Challenge
    @Author: Quentin Baker
    @Date: 9/20/2018
"""

import csv
import json
import sys
import time
import getopt

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

###############
# AWS IOT CONFIGURATION
###############

myMQTTClient = AWSIoTMQTTClient("ConnectedSensor")
myMQTTClient.configureEndpoint("a3u38y6be3pa0r.iot.us-east-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("certificates/CA.pem",
                                  "certificates/private.pem.key",
                                  "certificates/cert.pem.crt")

myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

################
# END AWS IOT CONFIG
################

timeStamp = 0

# Report window and interval defaults
windowSize = 4
intervalSize = 2

debug = True

def main(argv):
    # Parse command-line arguments
    try:
        opts, args = getopt.getopt(argv,"hdvw:i:", ["debug", "verbose", "help","window=","interval="])
    except getopt.GetoptError:
        print("DeviceEngine.py [-d] [-w] [-i]")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("DeviceEngine.py [-d] [-w] [-i]")
        elif opt in ("-d", "--debug", "-v", "--verbose"):
            global debug
            debug = True
        elif opt in ("-w", "--window"):
            global windowSize
            windowSize = arg
        elif opt in ("-i", "--interval"):
            global intervalSize
            intervalSize = arg

    pulldata()


def formatasjson(datalist):
    global debug

    if len(datalist) != 10:
        if debug:
            print("Error: Incorrect number of data values supplied.")
    else:
        json_payload = json.dumps({"timestamp": datalist[0],
                                  "min-temperature": datalist[1],
                                  "max-temperature": datalist[2],
                                  "avg-temperature": datalist[3],
                                  "min-humidity": datalist[4],
                                  "max-humidity": datalist[5],
                                  "avg-humidity": datalist[6],
                                  "min-pressure": datalist[7],
                                  "max-pressure": datalist[8],
                                  "avg-pressure": datalist[9]
                                  })

        if debug:
            print("JSON Payload created.")
        return json_payload


def publishtocloud(jsonpayload):
    global debug
    myMQTTClient.connect()

    if myMQTTClient.publish("things/ConnectedSensor/readings", jsonpayload, 0):
        if debug:
            print("Successfully published latest readings to AWS.")
    else:
        if debug:
            print("Failed to publish!")

    myMQTTClient.disconnect()


def pulldata():

    global debug
    global windowSize
    global intervalSize

    cur_window = 0
    cur_interval = 0

    mydatalist = [None] * 10

    temp_window = [None] * windowSize
    hmd_window = [0, 0, 0, 0]
    psi_window = [0, 0, 0, 0]

    max_temp, max_hmd, max_psi = (0, 0, 0)
    min_temp, min_hmd, min_psi = (sys.maxsize, sys.maxsize, sys.maxsize)

    with open('readings.csv', newline='') as csvFile:
        data_reader = csv.DictReader(csvFile)
        for row in data_reader:

            time.sleep(1)

            row_temp = float(row['temperature'])
            row_hmd = float(row['humidity'])
            row_psi = float(row['pressure'])
            mydatalist[0] = float(row['timestamp'])

            # Rolling window -- append the current temp to the modulo of the window size
            cur_pos = cur_window % windowSize
            temp_window[cur_pos] = row_temp
            hmd_window[cur_pos] = row_hmd
            psi_window[cur_pos] = row_psi

            # Update minimums
            if row_temp < min_temp:
                # min_temp
                min_temp = row_temp
                if debug:
                    print("New minimum temp:", min_temp)
            if row_hmd < min_hmd:
                # min_hmd
                min_hmd = row_hmd
                if debug:
                    print("New minimum humidity:", min_hmd)
            if row_psi < min_psi:
                # min_psi
                min_psi = row_psi
                if debug:
                    print("New minimum pressure:", min_psi)

            # Update maximums
            if row_temp > max_temp:
                # max_temp
                max_temp = row_temp
                if debug:
                    print("New maximum temp:", max_temp)
            if row_hmd > max_hmd:
                # max_hmd
                max_hmd = row_hmd
                if debug:
                    print("New maximum humidity:", max_hmd)
            if row_psi > max_psi:
                # max_psi
                max_psi = row_psi
                if debug:
                    print("New maximum pressure:", max_psi)

            # Update window and interval size
            cur_window += 1
            cur_interval += 1

            if (cur_interval % intervalSize) == 0 and cur_window >= windowSize:

                # minimum values
                mydatalist[1] = min_temp
                mydatalist[4] = min_hmd
                mydatalist[7] = min_psi

                # maximum values
                mydatalist[2] = max_temp
                mydatalist[5] = max_hmd
                mydatalist[8] = max_psi

                # average values
                mydatalist[3] = (sum(temp_window) / len(temp_window))
                mydatalist[6] = (sum(hmd_window) / len(hmd_window))
                mydatalist[9] = (sum(psi_window) / len(psi_window))

                if debug:
                    print("\n\n***Average data for last window***\n-Temp:",mydatalist[3], "\n-Humidity:", mydatalist[6],
                          "\n-Pressure:", mydatalist[9], "\n\n")

                publishtocloud(formatasjson(mydatalist))

                # reset data for next pull
                mydatalist = [None] * 10


if __name__ == "__main__":
    main(sys.argv[1:])

