#define LED 13
char rxChar= 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED, OUTPUT);
  Serial.flush();
}

void loop() {
  if (Serial.available() > 0){
    rxChar = Serial.read(); 
    Serial.flush();
  }

  switch (rxChar) {
    // Turn on
    case 'a':
    case 'A':
      digitalWrite(LED, HIGH);
      break;

    // Turn off
    case 'b':
    case 'B':
      digitalWrite(LED, LOW);
      break;
  }
}
