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
  gate.write(45);
  delay(1000);
  gate.write(0);

  // set IR as input
  pinMode(22, INPUT);
  pinMode(23, INPUT);

  // Set off LCD module
  lcd.init();
  lcd.backlight();

  // Start LED input
  pinMode(11, OUTPUT); //red
  pinMode(12, OUTPUT); //green
  pinMode(13, OUTPUT); //blue
  LEDLight(255,0,0);

  LCD(0,0,"System Ready...");
}

void loop() {
  if((digitalRead(22) == HIGH) && (GateStat == 0)){
      LEDLight(255,0,0);
      
      //LCDclean();
      LCD(0,0, "System Ready...");
  }
  if((digitalRead(22) == LOW) && (GateStat == 0)){
    LCDclean();
    LCD(0,2, "Vehicle Detected!");
    LEDLight(0,0,255);

    //delay 5 seconds to allow processing
    delay(5000);
    LCDclean();
    Serial.write('a');
  }
  if(Serial.available()>0){
    String phrase;
    x = Serial.read();
    
    if(x == 'b'){
      LEDLight(0,255,0);
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
  }
}

void LCD(int x, int y, String words){
  lcd.setCursor(x,y);
  lcd.print(words);
}

void LCDclean(){
  lcd.clear();
}

void LEDLight(int r, int g, int b){
  analogWrite(11, r);
  analogWrite(12, g);
  analogWrite(13, b);
}
