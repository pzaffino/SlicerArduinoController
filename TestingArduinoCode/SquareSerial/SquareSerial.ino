void setup() {
  Serial.begin(9600);
}

void loop() {
    
  for(int i=0;i<10;i++){
    Serial.print("0\n");
    delay(500);
  }

  for(int i=0;i<10;i++){
    Serial.print("255\n");
    delay(500);
  }
  
}
