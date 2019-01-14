// WiFi Configuration
const char* ssid = "MiFibra-2D79";
const char* password = "*******";

// MQTT Cibfiguration
const char* mqtt_server = "192.168.1.114";
const int mqtt_port = 1883;
const char* mqtt_id = "mainbedroom_sensor";
const char* mqtt_pub_topic_temperature = "/home/mainbedroom/temperature";
const char* mqtt_pub_topic_humidity = "/home/mainbedroom/humidity";
const char* mqtt_sub_topic_operation = "/home/mainbedroom/operation";

// Other params
const int update_time = 900000;
