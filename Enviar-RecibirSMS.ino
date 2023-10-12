#include <SoftwareSerial.h>

SoftwareSerial sim800lSerial(8, 9);  // RX, TX

void setup() {
  Serial.begin(9600);
  sim800lSerial.begin(9600);

  // Configurar el módulo SIM800L
  sim800lSerial.println("AT");
  sim800lSerial.println("AT+CSCS=\"IRA\"");
  delay(1000);
  sim800lSerial.println("AT+CMGF=1");  // Modo SMS
  delay(100);
  sim800lSerial.println("AT+CNMI=2,2,0,0,0");
}

void loop() {
  if (Serial.available()) {
    String telefono = Serial.readStringUntil('\n');  // Lee el número de teléfono desde Python
    String mensaje = Serial.readStringUntil('\n');  // Lee el mensaje desde Python

    sim800lSerial.print("AT+CMGS=\"");
    sim800lSerial.print(telefono);
    sim800lSerial.println("\"");

    delay(1000);

    sim800lSerial.print(mensaje);
    sim800lSerial.write(26);  // Envía el carácter Ctrl+Z para finalizar el SMS
    delay(1000);
  }

  if (sim800lSerial.available()) {
    String sms = sim800lSerial.readString();
    // Procesar el SMS y extraer datos
    // Aquí podrías usar técnicas de parsing para obtener los datos

    // Enviar datos a través de comunicación serial al servidor Python
    Serial.println("sms" + sms);
  }
}