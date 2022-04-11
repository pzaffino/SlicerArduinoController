// The number of the pushbutton pin
int buttonSET = 2;     
int buttonUP = 3;     
int buttonDOWN = 4;  

int buttonStateSET=0, buttonStateUP = 0, buttonStateDOWN=0;  // Variable for reading the pushbutton status

void setup() {
  pinMode(buttonSET, INPUT);
  pinMode(buttonUP, INPUT);
  pinMode(buttonDOWN, INPUT);
  Serial.begin(9600);

}

void loop() {

  buttonStateSET=digitalRead(buttonSET);
  buttonStateUP=digitalRead(buttonUP);
  buttonStateDOWN=digitalRead(buttonDOWN);

  if(buttonStateSET==HIGH){
    Serial.println(3); 
    delay(350);
  }

  if(buttonStateUP==HIGH){
    Serial.println(1); 
    delay(350);
  }
    
  if(buttonStateDOWN==HIGH){
    Serial.println(2); 
    delay(350);
  }
  
}
