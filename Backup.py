from APICommunication import apiCommunication
import json


class backup():
    def make_users_backup(self):
        api = apiCommunication()
        users = api.get_users()
        if users != "Error Exception":
            backup_file = open("backup_users.txt", 'w')
            line = ""
            for i in range(len(users)):
                json_users = json.loads(json.dumps(users[i]))
                line += (str(json_users["clearcode"]) + "\n") #pega o numero do cartao
            backup_file.write(line)
            backup_file.close()
            return True
        else:
            return False
