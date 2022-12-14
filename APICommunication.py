import json
import requests
import time


class apiCommunication():
    def __init__(self):
        self.user = "c4tr4c4"
        self.key = "YzR0cjRjNHA0c3N3MHJk"
        # self.url = "https://catracas.maracanau.com.br/"
        self.url = "https://api-v2.intranet.maracanau.ifce.edu.br/v1/integracao/transito/"

    def authenticate_card(self, card):
        url = self.url + "tag"
        querystring = {"cartao": str(card),
                       "usuario": str(self.user),
                       "senha": str(self.key)}
        try:
            requests.request("GET", url, params=querystring, timeout=10).json()
            print("passou")
            jsonResponse = json.loads(json.dumps(requests.request("GET", url, params=querystring, timeout=1).json()))
            print('chegou2')
            if (str(jsonResponse["autorizacao"]) == "1"):
                return True
            elif (str(jsonResponse["autorizacao"]) == "0"):
                return False
            else:
                return "Error authenticateCard"
        except Exception as e:
            print('chegou')
            print(e)
            return "Error Exception Authenticate"


    def post_user(self, numeroCatraca, tipoMovimentacao, cartao, data_hora):
        url = self.url + "inserirTransito"
        querystring = {"numeroCatraca": str(numeroCatraca),
                       "tipoMovimentacao": str(tipoMovimentacao),
                       "cartao": str(cartao),
                       "data_hora": str(data_hora),
                       "usuario": self.user,
                       "senha": self.key}             
        try:
            jsonResponse = json.loads(json.dumps(requests.request("POST", url, params=querystring, timeout=1).json()))
            if(str(jsonResponse["status"]) == "OK"):
                return True
            else:
                return False
        except Exception as e:
            return False

    def get_users(self):
        url = self.url + "backup"
        querystring = {"usuario": self.user,
                       "senha": self.key}
        try:
            jsonResponse = json.loads(json.dumps(requests.request("GET", url, params=querystring).json()))
            return jsonResponse
        except Exception as e:
            return "Error Exception"
