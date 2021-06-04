#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h> // Added library*

LiquidCrystal_I2C lcd(0x27, 20, 4);  // Set the LCD I2C address
Servo gate;
int pos, s2;
char x;
String plate;
int GateStat = 0;

void setup() {
  Serial.begin(9600);
  
  gate.attach(8);
  gate.write(0);
  gate.write(20);
  delay(500);
  gate.write(0);

  // set IR as input
  pinMode(22, INPUT);
  pinMode(23, INPUT);

  // Set off LCD module
  lcd.init();
  lcd.backlight();

  LCD(0,0,"System Ready...");
  LCD(3,3,"Status: CONNECTED");
}

void loop() {
  if((digitalRead(22) == LOW) && (GateStat == 0)){
    LCDclean();
    LCD(0,2, "Vehicle Detected!");

    //delay 5 seconds to allow processing
    delay(5000);
    
    Serial.write('a');
  }
  if(Serial.available()>0){
    String phrase;
    x = Serial.read();
    
    if(x == 'b'){
      GateStat = 1;
      plate = Serial.readStringUntil('\n');
      phrase = "Welcome " + plate;
      LCDclean();
      LCD(0,0,phrase);

      delay(250);
      gate.write(95);
    }
    if((x == 'c') && GateStat == 0){
      phrase = "   Entry blocked!   ";
      LCDclean();
      LCD(0,0,phrase);

      delay(5000);
      LCDclean();
      LCD(0,0, "System Ready...");
    }
    if((x == 'd') && GateStat == 0){
      phrase = "  Could not detect  ";
      LCDclean();
      LCD(0,0,phrase);
      phrase = "    plate number    ";
      LCD(0,1,phrase);
    }
  }
  if(digitalRead(23) == LOW){
    s2 = 1;
  }
  if((digitalRead(23) == HIGH) && s2 == 1){
    s2 = 0;
    gate.write(0);

    GateStat = 0;
    
    LCDclean();
    LCD(0,0, "System Ready...");
  }
}

void LCD(int x, int y, String words){
  lcd.setCursor(x,y);
  lcd.print(words);
}

void LCDclean(){
  lcd.clear();
}
