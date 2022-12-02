import json
import time
from APICommunication import apiCommunication
from datetime import datetime
from pytz import timezone
from Backup import backup

lista_usuarios = []
treadsRun = False
timestamp = datetime.timestamp(datetime.now())
# print(timestamp)

def getJsonUser(idCatraca, tipoMovimentacao, dadosEntrada):
    data_e_hora_atuais = datetime.now()
    fuso_horario = timezone("America/Sao_Paulo")
    data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
    data_e_hora_sao_paulo_em_texto = data_e_hora_sao_paulo.strftime("%Y-%m-%d %H:%M:%S")
    # data_e_hora_sao_paulo_em_texto = "10/10/2010"
    user = {"numeroCatraca": str(idCatraca), "tipoMovimentacao": str(tipoMovimentacao), "cartao": str(dadosEntrada), "data_hora": str(data_e_hora_sao_paulo_em_texto)}
    jsonUser = json.loads(json.dumps(user))
    return jsonUser

dadosEntrada = "06701243"
#dadosEntrada2 = "06715642"
#dadosEntradaNegada = "98765433"

jsonUser = getJsonUser("1", "2", dadosEntrada)
print(jsonUser)
#lista_usuarios.append(getJsonUser(1, 1, dadosEntrada))
#time.sleep(2)
#lista_usuarios.append(getJsonUser(3, 2, dadosEntrada2))

#lista_usuarios = str(getJsonUser(1, 1, dadosEntrada)) + ";" + str(getJsonUser(3, 0, dadosEntrada2))

#print(lista_usuarios)
api = apiCommunication()
# bk = backup()

print(api.authenticate_card(dadosEntrada))
#
#print(api.authenticate_card(dadosEntradaNegada))

#print(api.post_user(getJsonUser(1, 1, dadosEntrada)))
#print(jsonUser["cartao"])
#print(api.post_user(jsonUser["numeroCatraca"], jsonUser["tipoMovimentacao"], jsonUser["cartao"], jsonUser["data_hora"]))
#print(api.post_user(lista_usuarios))
#print(bk.make_users_backup())

# def make_log_users():
#     global timestamp, treadsRun
#     while True:
#         time.sleep(1)
#         timestamp_now = datetime.timestamp(datetime.now())
#         if ((timestamp_now - timestamp) > 10 and treadsRun == False):  # passou 30 minutos e nao ha ninguem passandp na catraca, evita conflito na lista de usuarios
#             timestamp = timestamp_now
#             print(timestamp)
#             grava_lista_post()
#
#
# def grava_lista_post():
#     global lista_usuarios
#     if (len(lista_usuarios) > 0):
#         log_file = open("log_users.txt", 'a+')
#         log_file.write(str(lista_usuarios).replace("[", "").replace("]","").replace("}", "}\n").replace(", {", "{"))
#         log_file.close()
#         lista_usuarios = []

# make_log_users()

