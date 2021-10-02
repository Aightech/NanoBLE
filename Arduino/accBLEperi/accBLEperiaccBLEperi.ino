
#include <ArduinoBLE.h>
#include <Arduino_LSM6DS3.h>//Arduino IOT

//#define DEBUG

#ifdef DEBUG
#define debug(x) Serial.print(x)
#define debugln(x) Serial.println(x)
#else
#define debug(x)
#define debugln(x)
#endif

BLEService nanoService("180F"); // BLE LED Service

// BLE LED Switch Characteristic - custom 128-bit UUID, read and writable by central
BLEDoubleCharacteristic accXCharacteristic("2A40", BLERead | BLENotify);
BLEDoubleCharacteristic accYCharacteristic("2A41", BLERead | BLENotify);
BLEDoubleCharacteristic accZCharacteristic("2A42", BLERead | BLENotify);


float x, y, z;

void setup() {
  #ifdef DEBUG
    Serial.begin(9600);
    while (!Serial);
  #endif

  // set LED pin to output mode
  pinMode(LED_BUILTIN, OUTPUT);
  // begin initialization
  if (!BLE.begin()) {
    debugln("starting BLE failed!");
    while (1);
  }

    // begin IMU initialization
  if (!IMU.begin()) {
    debugln("Failed to initialize IMU!");
    while (1);
  }

  // set advertised local name and service UUID:
  BLE.setLocalName("Arduino Nano 33 BLE Sense");
  BLE.setAdvertisedService(nanoService);

  // add the characteristic to the service
  nanoService.addCharacteristic(accXCharacteristic);
  nanoService.addCharacteristic(accYCharacteristic);
  nanoService.addCharacteristic(accZCharacteristic);

  // add service
  BLE.addService(nanoService);

  // start advertising
  BLE.advertise();
  debugln(BLE.address());
  debugln("BLE LED Peripheral");
}

// ------------------------------------------ VOID LOOP ------------------------------------------
void loop()
{
  // listen for BLE peripherals to connect:
  BLEDevice central = BLE.central();

  // if a central is connected to peripheral:
  if (central)
  {
    // while the central is still connected to peripheral:
    while (central.connected())
    {
        updateAcc();
    }
  }
}


void updateAcc()
{
  if (IMU.accelerationAvailable())
  {
    IMU.readAcceleration(x, y, z);
    char buffx[8], buffy[8], buffz[8];
    long t = millis();
    *( ((long*)&buffx)  ) = *(long*)&x;
    *( ((long*)&buffx)+1) = (*(long*)&t);
    *( ((long*)&buffy)  ) = *(long*)&y;
    *( ((long*)&buffy)+1) = (*(long*)&t);
    *( ((long*)&buffz)  ) = *(long*)&z;
    *( ((long*)&buffz)+1) = (*(long*)&t);
    accXCharacteristic.writeValue(*(double*)&buffx);
    accYCharacteristic.writeValue(*(double*)&buffy);
    accZCharacteristic.writeValue(*(double*)&buffz);
    debugln(String(x) + "\t" + String(y) + "\t" + String(z));
  }
}
