import json
from APICommunication import apiCommunication


class LogUsers:
    path = "/share/ControleAcessoCatraca/"

    def record_user_list(self, lista_usuarios):
        if (len(lista_usuarios) > 0):
            log_file = open(self.path + "log_users.txt", 'a+')
            log_file.write(
                str(lista_usuarios).replace("[", "").replace("]", "").replace("}", "}\n").replace(", {", "{").replace("'", "\""))
            log_file.close()

    def post_log_users(self):
        read_log_users = open(self.path + "log_users.txt", 'r')
        api = apiCommunication()
        lines = read_log_users.readlines()
        new_lines = lines.copy()
        print(len(lines))
        print(len(new_lines))
        for line in lines:
            jsonUser = json.loads(line)
            x = api.post_user(jsonUser['numeroCatraca'], jsonUser['tipoMovimentacao'], jsonUser['cartao'], jsonUser['data_hora'])
            if x:
                new_lines.remove(line)
        read_log_users.close()
        write_log_users = open(self.path + "log_users.txt", 'w')
        write_log_users.writelines(new_lines)
        write_log_users.close()
