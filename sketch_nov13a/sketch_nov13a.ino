#define POTENTIOMETER_PIN A0
int num_global = 0;

void setup() 
{
  Serial.begin(9600);
}
void loop()
{
  float var = analogRead(POTENTIOMETER_PIN);
  float value = map(var,0,1023,0,200);
  int num = int(value);
  if (num != num_global){
    num_global = num;
    Serial.println(num);

  }
  delay(500);
}
