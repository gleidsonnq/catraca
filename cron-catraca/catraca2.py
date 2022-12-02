import serial
import time
import threading
import RPi.GPIO as gpio
import sys
import difflib
import pigpio
import os

#gpio.cleanup()

os.system("kill -9 $(ps aux | grep -m 1 pigpiod | tr -s ' '| cut -d' ' -f2)") #mata o processo pigpiod
os.system("kill -9 $(ps aux | grep -m 1 catraca | grep -w Tl | tr -s ' '| cut -d' ' -f2)") #mata o processo da catraca
os.system("sudo pigpiod")

gpio.setwarnings(False)
#RX padrao = GPIO15
RX_entrada=26
####
flagEntrada = True #se false entao e saida
LED_VERDE_SAIDA = 21
LED_VERDE_ENTRADA = 20 #JA TAVA
REED_SWITCH_ENTRADA = 23
REED_SWITCH_SAIDA = 24
RELE_ENTRADA = 12
RELE_SAIDA = 16
SEGUNDOS_CASO1_ACESSO_NEGADO =3
# BUZZER = 7
#######

gpio.setmode(gpio.BCM)

gpio.setup(REED_SWITCH_ENTRADA, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(REED_SWITCH_SAIDA, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(RELE_SAIDA, gpio.OUT)
gpio.setup(RELE_ENTRADA, gpio.OUT)
gpio.setup(LED_VERDE_SAIDA, gpio.OUT)
gpio.setup(LED_VERDE_ENTRADA, gpio.OUT)
# gpio.setup(BUZZER, gpio.OUT)
# gpio.output(BUZZER, gpio.HIGH)

treadsRun = False
contCaso1 = 0

PortRF = serial.Serial('/dev/ttyS0', 9600, timeout = 1) # ttyACM1 for Arduino board

dadosEntrada = 0   #chars waiting from laser range finder

def hexToWiegand(tagHex):
    facility = "";
    cardCode = "";

    facility += str(tagHex[4])
    facility += str(tagHex[5])
    cardCode += str(tagHex[6])
    cardCode += str(tagHex[7])
    cardCode += str(tagHex[8])
    cardCode += str(tagHex[9])
	
    facility = facility.replace("b","").replace("'","")
    cardCode = cardCode.replace("b","").replace("'","")
	
    #print(facility)
    #print(cardCode)

    facility = hexToDec(facility)
    cardCode = hexToDec(cardCode)
	
    while(len(facility) < 3):
       facility = "0"+facility
    while(len(cardCode) < 5):
       cardCode = "0"+cardCode

    return (facility+cardCode)

def verificaTag(dadosEntrada):
	with open("/share/a.txt", "r") as myfile:
		lines = myfile.readlines()
	# print(lines)
	# print(len(lines))
	for i in range(len(lines)):
		# print(i)
		# print(lines[i][0:8])
		# print(dadosEntrada)
		if(lines[i][0:8]==(dadosEntrada)):
			return True
	return False
	myfile.close()

# def buzzerOK():
# 	for i in range(3):
# 		gpio.output(BUZZER, gpio.LOW)
# 		time.sleep(0.1)
# 		gpio.output(BUZZER, gpio.HIGH)
# 		time.sleep(0.1)

# def buzzerErro():
# 	gpio.output(BUZZER, gpio.LOW)
# 	time.sleep(0.6)
# 	gpio.output(BUZZER, gpio.HIGH)


def validaAcesso(entrada, dadosEntrada):
	global treadsRun, flagEntrada
	if verificaTag(dadosEntrada):
		print("acesso liberado!!")
		if(entrada):
			gpio.output(RELE_ENTRADA, gpio.LOW)
			gpio.output(LED_VERDE_ENTRADA, gpio.LOW)
		else:
			gpio.output(RELE_SAIDA, gpio.LOW)
			gpio.output(LED_VERDE_SAIDA, gpio.LOW)
		# print("flagggg!")
		treadsRun = True
		flagEntrada = entrada
		# buzzerOK()
	else:
		print("acesso negado")
		time.sleep(SEGUNDOS_CASO1_ACESSO_NEGADO)
		# buzzerErro()

def hexToDec(value):
	i = int(value, 16)
	return str(i)


#mantem a catraca aberta por 5 segundos
def caso1():
	global treadsRun, flagEntrada
	while True:
	    if treadsRun == True :
		    time.sleep(1)
		    contCaso1 = contCaso1 + 1
		    # print("treading caso1...")
		    if contCaso1 >= SEGUNDOS_CASO1_ACESSO_NEGADO:
		    	if(flagEntrada):
		    		gpio.output(RELE_ENTRADA, gpio.HIGH)
		    		gpio.output(LED_VERDE_ENTRADA, gpio.HIGH)
		    	else:
		    		gpio.output(RELE_SAIDA, gpio.HIGH)
		    		gpio.output(LED_VERDE_SAIDA, gpio.HIGH)
		    	treadsRun = False
		    	
	    else:
		    time.sleep(1)
			#print("else caso 1")
		    contCaso1 = 0


#alguem termina de passar
def caso2():
	global treadsRun, flagEntrada
	while True:
	    if treadsRun == True :
		    time.sleep(0.1)
		    # print("treading caso2...")
		    if(flagEntrada):
			    if gpio.input(REED_SWITCH_ENTRADA) == 1:
			    	gpio.output(RELE_ENTRADA, gpio.HIGH)
			    	treadsRun = False
			    	gpio.output(LED_VERDE_ENTRADA, gpio.HIGH)
		    else:
		    	if gpio.input(REED_SWITCH_SAIDA) == 1:
		    		gpio.output(RELE_SAIDA, gpio.HIGH)
		    		treadsRun = False
		    		gpio.output(LED_VERDE_SAIDA, gpio.HIGH)

	    else:
		    time.sleep(1)
	            #print("else caso 2")





try:
	t = threading.Thread(target=caso1)
	t.start()
	t2 = threading.Thread(target=caso2)
	t2.start()
except:
   print ("Error: unable to start thread")

try:
	pi = pigpio.pi()
	pi.set_mode(RX_entrada, pigpio.INPUT)
	pi.bb_serial_read_open(RX_entrada, 9600, 8)
	gpio.output(RELE_ENTRADA, gpio.HIGH)
	gpio.output(RELE_SAIDA, gpio.HIGH)
	gpio.output(LED_VERDE_ENTRADA, gpio.HIGH)
	gpio.output(LED_VERDE_SAIDA, gpio.HIGH)
except Exception as e:
	if(str(e) == "\'NoneType\' object has no attribute \'send\'"):
			os.system("reboot")

while True:
	try:
		#leitura software serial
		(count, data) = pi.bb_serial_read(RX_entrada)
		if count:
			#print(count)
			#print(str(data).replace("bytearray","").replace("b'",""))
			tagCompleteList = list(str(data).replace("bytearray","").replace("b'",""))
			tagSaidaList = [tagCompleteList[5], tagCompleteList[6], tagCompleteList[7], tagCompleteList[8], tagCompleteList[9],  tagCompleteList[10], tagCompleteList[11], tagCompleteList[12], tagCompleteList[13], tagCompleteList[14]]
			# print("Saida: ")
			# print(tagSaidaList)
			dadosTagSaida = hexToWiegand(tagSaidaList) 
			print("Saida: " + dadosTagSaida)
			validaAcesso(False, dadosTagSaida)
			count=0
			data=""
			pi.bb_serial_read_close(RX_entrada)
			# time.sleep(3)
			while(treadsRun):
				time.sleep(0.1)
			pi.bb_serial_read_open(RX_entrada, 9600, 8)
        
		#leitura hardware serial
		tag = []
		read_byte = PortRF.read()
		if  (read_byte==(b'\x02')):
			for Counter in range(12):
				read_byte=PortRF.read()
				tag.append(str(read_byte))
			# print("Entrada: ")
			# print(tag)
			dadosTagEntrada = hexToWiegand(tag) 
			print("Entrada: " + dadosTagEntrada)
			validaAcesso(True, dadosTagEntrada)
			# time.sleep(3)
			while(treadsRun):
				time.sleep(0.1)
		#ser.flush()
		#count.flush()
		#read_byte = ""
		PortRF.flushInput()
		#pi.flushInput()
	except:
		print("Falha no Loop")
		time.sleep(0.5)
		pass
 #flush the buffer


#a catraca fica aberta por 5 segundos



