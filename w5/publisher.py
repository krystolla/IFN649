import paho.mqtt.publish as publish

publish.single("ifn649", "LED_OFF", hostname="13.211.13.221")
print("Done")
