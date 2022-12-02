import serial
import time
import threading
import RPi.GPIO as gpio
import sys
import difflib
import pigpio
import os
import datetime
from datetime import datetime
from pytz import timezone
import json
from APICommunication import apiCommunication
from LogUsers import LogUsers
api = apiCommunication()
log_users = LogUsers()

idCatraca = 1
os.system("kill -9 $(ps aux | grep -m 1 catraca | grep -w Tl | tr -s ' '| cut -d' ' -f2)") #mata o processo da catraca
time.sleep(1)

gpio.setwarnings(False)

flagEntrada = True #se false entao e saida
LED_VERDE_RELE_SAIDA = 21
LED_VERDE_RELE_ENTRADA = 20
LED_RGB_AZUL_ENTRADA = 22
LED_RGB_AZUL_SAIDA = 27
LED_RGB_VERMELHO_ENTRADA = 6
LED_RGB_VERMELHO_SAIDA = 5
LED_RGB_VERDE_ENTRADA = 19
LED_RGB_VERDE_SAIDA = 13
REED_SWITCH_ENTRADA = 23
TEMPO_GRAVACAO_ARQUIVO = 1800
REED_SWITCH_SAIDA = 24
RELE_ENTRADA = 12
RELE_SAIDA = 16
SEGUNDOS_CASO1_ACESSO_NEGADO =3
lista_usuarios = []
#######

gpio.setmode(gpio.BCM)

gpio.setup(REED_SWITCH_ENTRADA, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(REED_SWITCH_SAIDA, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(RELE_SAIDA, gpio.OUT)
gpio.setup(RELE_ENTRADA, gpio.OUT)
gpio.setup(LED_VERDE_RELE_SAIDA, gpio.OUT)
gpio.setup(LED_VERDE_RELE_ENTRADA, gpio.OUT)
gpio.setup(LED_RGB_AZUL_ENTRADA, gpio.OUT)
gpio.setup(LED_RGB_AZUL_SAIDA, gpio.OUT)
gpio.setup(LED_RGB_VERDE_ENTRADA, gpio.OUT)
gpio.setup(LED_RGB_VERDE_SAIDA, gpio.OUT)
gpio.setup(LED_RGB_VERMELHO_ENTRADA, gpio.OUT)
gpio.setup(LED_RGB_VERMELHO_SAIDA, gpio.OUT)

treadsRun = False
contCaso1 = 0
timestamp = datetime.timestamp(datetime.now())

usb0 = False

def usb_serial_connect():
	global usb0
	try:
		if usb0:
			usb0 = False
			usb_serial = serial.Serial('/dev/ttyUSB1', 9600, timeout = 1)
		else:
			usb0 = True
			usb_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
		return usb_serial
	except Exception as e:
		print(e)
		time.sleep(5)
		return usb_serial_connect()



PortRF = serial.Serial('/dev/ttyS0', 9600, timeout = 1) # ttyACM1 for Arduino board
usb_serial = usb_serial_connect()

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



    facility = hexToDec(facility)
    cardCode = hexToDec(cardCode)

    while(len(facility) < 3):
       facility = "0"+facility
    while(len(cardCode) < 5):
       cardCode = "0"+cardCode

    return (facility+cardCode)


def verificaTagRequest(dadosEntrada):
	request = api.authenticate_card(dadosEntrada)
	if(type(request)==bool): #nao deu erro na requisicao
		return request
	else: #se der erro na requisicao, nosso sistema continua funcionando de forma independente
		with open("/share/develop/catraca_ifce_maracanau/backup_users.txt", "r") as myfile:
			lines = myfile.readlines()

			for i in range(len(lines)):
				if(int(lines[i])==int(dadosEntrada)):
					return True
			return False
			myfile.close()


def registraLogRequest(dadosEntrada,entrada,idCatraca):
	# entrada -> true para entrada e false para saida
	# dadosEntrada -> numero do cartao rfid
	# idCatraca -> numero da catraca
	global lista_usuarios

	data_e_hora_atuais = datetime.now()
	fuso_horario = timezone("America/Sao_Paulo")
	data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
	data_e_hora_sao_paulo_em_texto = data_e_hora_sao_paulo.strftime("%d/%m/%Y %H:%M:%S")

	if(entrada):
		tipoMovimentacao = 1
	else:
		tipoMovimentacao = 2
	post_api_ok = api.post_user(str(idCatraca), str(tipoMovimentacao), str(dadosEntrada), str(data_e_hora_sao_paulo_em_texto))

	if(post_api_ok == False):
		user = {"numeroCatraca": str(idCatraca), "tipoMovimentacao": str(tipoMovimentacao), "cartao": str(dadosEntrada),"data_hora": str(data_e_hora_sao_paulo_em_texto)}
		jsonUser = json.loads(json.dumps(user))
		lista_usuarios.append(jsonUser)



def validaAcesso(entrada, dadosEntrada):
	global treadsRun, flagEntrada, idCatraca
	if verificaTagRequest(dadosEntrada):
		if(entrada):
			gpio.output(RELE_ENTRADA, gpio.LOW)
			gpio.output(LED_VERDE_RELE_ENTRADA, gpio.LOW)
			gpio.output(LED_RGB_AZUL_ENTRADA, gpio.LOW)
			gpio.output(LED_RGB_VERMELHO_ENTRADA, gpio.LOW)
			gpio.output(LED_RGB_VERDE_ENTRADA, gpio.HIGH)
		else:
			gpio.output(RELE_SAIDA, gpio.LOW)
			gpio.output(LED_VERDE_RELE_SAIDA, gpio.LOW)
			gpio.output(LED_RGB_AZUL_SAIDA, gpio.LOW)
			gpio.output(LED_RGB_VERMELHO_SAIDA, gpio.LOW)
			gpio.output(LED_RGB_VERDE_SAIDA, gpio.HIGH)
		treadsRun = True
		flagEntrada = entrada
	else:
		if(entrada):
			gpio.output(LED_RGB_AZUL_ENTRADA, gpio.LOW)
			gpio.output(LED_RGB_VERDE_ENTRADA, gpio.LOW)
			gpio.output(LED_RGB_VERMELHO_ENTRADA, gpio.HIGH)
			time.sleep(SEGUNDOS_CASO1_ACESSO_NEGADO)
			gpio.output(LED_RGB_VERMELHO_ENTRADA, gpio.LOW)
			gpio.output(LED_RGB_AZUL_ENTRADA, gpio.HIGH)

		else:
			gpio.output(LED_RGB_AZUL_SAIDA, gpio.LOW)
			gpio.output(LED_RGB_VERDE_SAIDA, gpio.LOW)
			gpio.output(LED_RGB_VERMELHO_SAIDA, gpio.HIGH)
			time.sleep(SEGUNDOS_CASO1_ACESSO_NEGADO)
			gpio.output(LED_RGB_VERMELHO_SAIDA, gpio.LOW)
			gpio.output(LED_RGB_AZUL_SAIDA, gpio.HIGH)

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
			if contCaso1 >= SEGUNDOS_CASO1_ACESSO_NEGADO:
				if(flagEntrada):
					gpio.output(RELE_ENTRADA, gpio.HIGH)
					gpio.output(LED_VERDE_RELE_ENTRADA, gpio.HIGH)
					gpio.output(LED_RGB_VERDE_ENTRADA, gpio.LOW)
					gpio.output(LED_RGB_VERMELHO_ENTRADA, gpio.LOW)
					gpio.output(LED_RGB_AZUL_ENTRADA, gpio.HIGH)
				else:
					gpio.output(RELE_SAIDA, gpio.HIGH)
					gpio.output(LED_VERDE_RELE_SAIDA, gpio.HIGH)
					gpio.output(LED_RGB_VERDE_SAIDA, gpio.LOW)
					gpio.output(LED_RGB_VERMELHO_SAIDA, gpio.LOW)
					gpio.output(LED_RGB_AZUL_SAIDA, gpio.HIGH)
				treadsRun = False

		else:
			time.sleep(1)
			contCaso1 = 0


#alguem termina de passar
def caso2():
	global treadsRun, flagEntrada, dadosTagSaida, dadosTagEntrada, idCatraca
	while True:
		if treadsRun == True :
			time.sleep(0.05)
			if(flagEntrada):
				if gpio.input(REED_SWITCH_ENTRADA) == 1:
					gpio.output(RELE_ENTRADA, gpio.HIGH)
					gpio.output(LED_VERDE_RELE_ENTRADA, gpio.HIGH)
					gpio.output(LED_RGB_VERDE_ENTRADA, gpio.LOW)
					gpio.output(LED_RGB_VERMELHO_ENTRADA, gpio.LOW)
					gpio.output(LED_RGB_AZUL_ENTRADA, gpio.HIGH)
					registraLogRequest(dadosTagEntrada,flagEntrada,idCatraca)
					treadsRun = False
			else:
				if gpio.input(REED_SWITCH_SAIDA) == 1:
					gpio.output(RELE_SAIDA, gpio.HIGH)
					gpio.output(LED_VERDE_RELE_SAIDA, gpio.HIGH)
					gpio.output(LED_RGB_VERDE_SAIDA, gpio.LOW)
					gpio.output(LED_RGB_VERMELHO_SAIDA, gpio.LOW)
					gpio.output(LED_RGB_AZUL_SAIDA, gpio.HIGH)
					registraLogRequest(dadosTagSaida, flagEntrada, idCatraca)
					treadsRun = False

		else:
			time.sleep(1)

def make_log_users():
	global timestamp, treadsRun
	while True:
		time.sleep(5)
		timestamp_now = datetime.timestamp(datetime.now())
		if((timestamp_now-timestamp)>TEMPO_GRAVACAO_ARQUIVO and treadsRun==False): 	#passou 30 minutos e nao ha ninguem passandp na catraca, evita conflito na lista de usuarios
			timestamp = timestamp_now
			global lista_usuario
			log_users.record_user_list(lista_usuarios)
			lista_usuarios = []


try:
	t = threading.Thread(target=caso1)
	t.start()
	t2 = threading.Thread(target=caso2)
	t2.start()
	t3 = threading.Thread(target=make_log_users)
	t3.start()
except:
   print ("Error: unable to start thread")

try:
	gpio.output(RELE_ENTRADA, gpio.HIGH)
	gpio.output(RELE_SAIDA, gpio.HIGH)
	gpio.output(LED_VERDE_RELE_ENTRADA, gpio.HIGH)
	gpio.output(LED_VERDE_RELE_SAIDA, gpio.HIGH)
	gpio.output(LED_RGB_AZUL_ENTRADA, gpio.HIGH)
	gpio.output(LED_RGB_AZUL_SAIDA, gpio.HIGH)
	gpio.output(LED_RGB_VERMELHO_ENTRADA, gpio.LOW)
	gpio.output(LED_RGB_VERMELHO_SAIDA, gpio.LOW)
	gpio.output(LED_RGB_VERDE_ENTRADA, gpio.LOW)
	gpio.output(LED_RGB_VERDE_SAIDA, gpio.LOW)
except Exception as e:
	print(e)

while True:
	try:
		#leitura usb serial para SAIDA
		usb_tag = []
		usb_read_byte = usb_serial.read()
		if  (usb_read_byte==(b'\x02')):
			for Counter in range(12):
				usb_read_byte=usb_serial.read()
				usb_tag.append(str(usb_read_byte))
			dadosTagSaida = hexToWiegand(usb_tag)
			if(dadosTagSaida != "00000000"):
				validaAcesso(False, dadosTagSaida)
			while(treadsRun):
				time.sleep(0.1)
		usb_serial.flushInput()

		#leitura hardware serial para ENTRADA
		tag = []
		read_byte = PortRF.read()
		if  (read_byte==(b'\x02')):
			for Counter in range(12):
				read_byte=PortRF.read()

				tag.append(str(read_byte))
			dadosTagEntrada = hexToWiegand(tag)
			if(dadosTagEntrada != "00000000"):
				validaAcesso(True, dadosTagEntrada)
			while(treadsRun):
				time.sleep(0.1)
		PortRF.flushInput()
	except Exception as e:
		time.sleep(0.5)
		usb_serial = usb_serial_connect()
		pass

