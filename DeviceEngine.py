""" Python solution attempt for the SpinDance Code Challenge
    @Author: Quentin Baker
    @Date: 9/20/2018
"""

# Import SDK packages
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

print("Running...")

###############
# CONFIGURATION
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
# END CONFIG
################

def fireOnPub(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


myMQTTClient.connect()
time.sleep(1)

print("Test publishing...")

if myMQTTClient.publish("testTopic", "myPayload", 0):
    print("Pub success!")

myMQTTClient.disconnect()
