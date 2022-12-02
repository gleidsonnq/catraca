from datetime import datetime
from pytz import timezone
import json

data_e_hora_atuais = datetime.now()
fuso_horario = timezone("America/Sao_Paulo")
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
data_e_hora_sao_paulo_em_texto = data_e_hora_sao_paulo.strftime("%d/%m/%Y %H:%M:%S")

print(data_e_hora_sao_paulo_em_texto)

idCatraca = "1"
tipoMovimentacao = "1"
dadosEntrada = "3938383"
lista_usuarios = []


user = {"numeroCatraca":str(idCatraca), "tipoMovimentacao":str(tipoMovimentacao), "cartao":str(dadosEntrada), "data_hora":str(data_e_hora_sao_paulo_em_texto)}

jsonUser = json.loads(json.dumps(user))
lista_usuarios.append(jsonUser)

idCatraca = "0"
tipoMovimentacao = "0"
dadosEntrada = "8373622"
user2 = {"numeroCatraca":str(idCatraca), "tipoMovimentacao":str(tipoMovimentacao), "cartao":str(dadosEntrada), "data_hora":str(data_e_hora_sao_paulo_em_texto)}


jsonUser2 = json.loads(json.dumps(user2))
lista_usuarios.append(jsonUser2)

print(lista_usuarios)
