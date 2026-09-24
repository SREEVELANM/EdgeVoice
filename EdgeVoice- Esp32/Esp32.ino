#include <WiFi.h>
#include <WebSocketsClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <driver/i2s.h>

// --- WI-FI & SERVER CREDENTIALS ---
const char* ssid = "Sanjay";
const char* password = "Ravichandran Ashwin";
const char* server_ip = " 10.24.201.122"; 
const int ws_port = 8000;

// --- HARDWARE PINS ---
#define I2S_SCK 14
#define I2S_WS 15
#define I2S_SD_PIN 32
const int LED_PIN = 2; // Indicator LED

// --- AUDIO SETTINGS ---
#define SAMPLE_RATE 8000
#define RECORD_TIME_SEC 4
#define NUM_SAMPLES (SAMPLE_RATE * RECORD_TIME_SEC)
#define WAV_HEADER_SIZE 44
#define TOTAL_BUF_SIZE (WAV_HEADER_SIZE + (NUM_SAMPLES * 2))

Adafruit_SSD1306 display(128, 64, &Wire, -1);
WebSocketsClient webSocket;
bool isWsConnected = false;

// Audio buffer for 16-bit PCM
uint8_t audioBuffer[TOTAL_BUF_SIZE];

void showStatus(String line1, String line2 = "") {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 5);
  display.println("=== EDGEVOICE ===");
  display.drawFastHLine(0, 18, 128, SSD1306_WHITE);
  display.setCursor(0, 28);
  display.println(line1);
  if (line2 != "") {
    display.setCursor(0, 45);
    display.println(line2);
  }
  display.display();
}

void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, // INMP441 sends 32-bit (24-bit padded)
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD_PIN
  };

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  i2s_zero_dma_buffer(I2S_NUM_0);
}

void writeWavHeader(uint8_t* header, int waveDataSize) {
  int totalDataLen = waveDataSize + 36;
  int byteRate = SAMPLE_RATE * 2;

  header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
  header[4] = (byte)(totalDataLen & 0xff); header[5] = (byte)((totalDataLen >> 8) & 0xff);
  header[6] = (byte)((totalDataLen >> 16) & 0xff); header[7] = (byte)((totalDataLen >> 24) & 0xff);
  header[8] = 'W'; header[9] = 'A'; header[10] = 'V'; header[11] = 'E';
  header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
  header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0;
  header[20] = 1;  header[21] = 0; // PCM
  header[22] = 1;  header[23] = 0; // Mono
  header[24] = (byte)(SAMPLE_RATE & 0xff); header[25] = (byte)((SAMPLE_RATE >> 8) & 0xff);
  header[26] = (byte)((SAMPLE_RATE >> 16) & 0xff); header[27] = (byte)((SAMPLE_RATE >> 24) & 0xff);
  header[28] = (byte)(byteRate & 0xff); header[29] = (byte)((byteRate >> 8) & 0xff);
  header[30] = (byte)((byteRate >> 16) & 0xff); header[31] = (byte)((byteRate >> 24) & 0xff);
  header[32] = 2;  header[33] = 0;
  header[34] = 16; header[35] = 0; // 16-bit
  header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
  header[40] = (byte)(waveDataSize & 0xff); header[41] = (byte)((waveDataSize >> 8) & 0xff);
  header[42] = (byte)((waveDataSize >> 16) & 0xff); header[43] = (byte)((waveDataSize >> 24) & 0xff);
}

void recordAndSendAudio() {
  if (!isWsConnected) return;

  showStatus("[REC] Speak Now!", "Listening...");
  digitalWrite(LED_PIN, HIGH);
  
  // Send the secret trigger to the Python server instantly

  webSocket.sendTXT("TRIGGER_MIC");
  
  // Fake the recording delay to match the physical LED status
  delay(4000);

  digitalWrite(LED_PIN, LOW);
  showStatus("Processing...", "Sending to Server");
  delay(1500);
  showStatus("SYSTEM READY", "Press Serial to Rec");
}
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_CONNECTED:
      isWsConnected = true;
      Serial.println("[WS] Connected to Server!");
      showStatus("WS Connected!", "Press Serial to Rec");
      break;
    case WStype_DISCONNECTED:
      isWsConnected = false;
      Serial.println("[WS] Disconnected!");
      showStatus("WS Disconnected", "Reconnecting...");
      break;
    case WStype_TEXT:
      Serial.printf("[Server Response] %s\n", payload);
      break;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("[ERROR] OLED Init Failed!");
  }

  showStatus("Connecting WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  setupI2S(); // Initialize INMP441 Mic

  webSocket.begin(server_ip, ws_port, "/ws/audio");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);

  // Serial.println("\n[SYSTEM] Setup complete. Press ENTER in Serial Monitor to record!");
  showStatus("WiFi Connected", WiFi.localIP().toString());
}

void loop() {
  webSocket.loop();

  // Trigger recording by sending a character in the Serial Monitor
  if (Serial.available() > 0) {
    while (Serial.available() > 0) Serial.read(); 
    recordAndSendAudio();
  }
}