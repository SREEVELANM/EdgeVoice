# EdgeVoice: Low Latency Voice Activator for Edge Devices

EdgeVoice is a hybrid edge-to-cloud IoT voice automation system developed for the Smart India Hackathon 2026 (PS ID: SIH26172). It bypasses continuous cloud audio streaming by leveraging a local area network to process speech intents, drastically reducing latency and enhancing user privacy.

This repository contains the FastAPI Python backend and the ESP32 C++ firmware. The system utilizes WebSockets for instant trigger communication and an MQTT broker for executing physical hardware commands.

---

## 🚀 Key Features

* **Local PC Automation:** Instantly launch applications (Camera, Calculator, VLC, Notepad) via voice without cloud processing delays.
* **Hardware Telemetry & Control:** Toggle physical edge devices (LEDs/Relays) via MQTT and display real-time sensor data on an OLED screen.
* **Offline Text-to-Speech (TTS):** Uses `pyttsx3` to speak real-time environmental data (Temperature & Humidity) directly from the edge node.
* **Dynamic Web Routing:** Parses natural language queries to isolate search terms and instantly execute web searches.
* **Resilient Architecture:** Includes auto-reconnect logic for WebSockets and exception handling for dropped network connections.

---

## 🏗️ System Architecture

1. **Trigger:** The ESP32 edge node initiates the sequence via a WebSocket text trigger (`TRIGGER_MIC`) sent to the local server.
2. **Audio Capture:** The Python backend captures audio using `speech_recognition`, automatically adjusting for ambient room noise.
3. **Intent Parsing:** The server parses the transcript to determine if the command is meant for the local host PC or the edge hardware.
4. **Execution:**
* *Local Action:* Executes `os.system` or `subprocess.Popen` for PC applications.
* *Hardware Action:* Publishes a JSON payload to `edgevoice/hardware` via MQTT (test.mosquitto.org) which the ESP32 intercepts to toggle physical pins.



---

## 🔌 Hardware Pinout (ESP32)

### 1. OLED Display (0.96" I2C)
| Component Pin | ESP32 Pin | Notes |
| :--- | :--- | :--- |
| **SDA** | GPIO 26 | Custom I2C data pin to avoid bus conflicts. |
| **SCL / SCK** | GPIO 27 | Custom I2C clock pin. |
| **VDD / VCC** | 3.3V | Ensure stable power connection. |
| **GND** | GND | Common ground. |

### 2. INMP441 I2S Microphone
| Component Pin | ESP32 Pin | Notes |
| :--- | :--- | :--- |
| **VDD** | 3.3V | Power for the microphone. |
| **GND** | GND | Common ground. |
| **L/R** | GND | Grounding this pin sets the mic to the Left Channel. |
| **WS** (Word Select) | GPIO 15 | I2S Word Select (Left/Right Clock). |
| **SCK** (Serial Clock) | GPIO 14 | I2S Continuous Serial Clock. |
| **SD** (Serial Data) | GPIO 32 | I2S Serial Data Output. |

### 3. DHT11 Temperature & Humidity Sensor
| Component Pin | ESP32 Pin | Notes |
| :--- | :--- | :--- |
| **VCC / + / Middle** | 3.3V (or VIN/5V) | Power (Swap to 5V if sensor reads NaN). |
| **GND / -** | GND | Common ground. |
| **DATA / S / OUT** | GPIO 4 | Digital data pin (moved off GPIO 5 to prevent boot issues). |

### 4. Status Indicator
| Component Pin | ESP32 Pin | Notes |
| :--- | :--- | :--- |
| **LED Positive** | GPIO 2 | Built-in or external LED for recording status feedback. |

---

## 💻 Software Setup & Installation

### 1. Python Backend setup

Ensure you have Python 3.9+ installed. Activate your virtual environment and install the required dependencies:

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install fastapi uvicorn speechrecognition pyaudio paho-mqtt pyttsx3 numpy

```

### 2. ESP32 Firmware Setup

Open the Arduino IDE and ensure the following libraries are installed via the Library Manager:

* `WebSockets` by Markus Sattler
* `Adafruit GFX Library` by Adafruit
* `Adafruit SSD1306` by Adafruit

Update the Wi-Fi credentials and the `server_ip` in the `.ino` sketch to match the IPv4 address of the machine running the FastAPI server.

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* server_ip = "192.168.X.X"; 

```

### 3. Launching the System

Start the FastAPI server from your terminal:

```powershell
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

```

Power on the ESP32. The OLED will display "WiFi Connected" followed by "SYSTEM READY".

---

## 🎙️ Supported Voice Commands

Press **Enter** in the Arduino Serial Monitor to trigger the listening phase, then speak one of the following commands:

| Intent Category | Voice Command Trigger | Action Performed |
| --- | --- | --- |
| **Hardware Control** | *"Turn on the LED"* | Publishes MQTT command; ESP32 lights the LED. |
| **Environment** | *"What is the temperature?"* | Server reads simulated edge data and speaks it aloud. |
| **PC Automation** | *"Open Camera"* | Launches the Windows Camera application. |
| **PC Automation** | *"Open Calculator"* | Launches the Windows Calculator. |
| **PC Automation** | *"Open Notepad"* | Launches Notepad. |
| **Media Control** | *"Play Video"* or *"Open VLC"* | Launches VLC in fullscreen playing the demo `.mp4`. |
| **Web Search** | *"Search [Query]"* | Isolates the query and opens Google Search in the browser. |

---

## 🛠️ Troubleshooting

* **Server Crash (WinError 10065):** This indicates the host PC has lost its internet connection, which is required for the transcription API. Check your mobile hotspot.
* **OLED Screen is Black:** Verify the I2C address is `0x3C`. Ensure the custom SDA (26) and SCL (27) pins are wired correctly and firmly seated in the breadboard.
* **VLC Not Found:** If the "Play Video" command fails, ensure VLC is installed at `C:\Program Files\VideoLAN\VLC\vlc.exe` and update the `video_path` in `main.py` to point to a valid file.

---

**Developed by Team The Rookiez**

Smart India Hackathon 2026*
