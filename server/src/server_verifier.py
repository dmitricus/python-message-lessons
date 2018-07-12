# метакласс ServerVerifier, выполняющий базовую проверку класса Сервер:
# - отсутствие вызовов connect для сокетов;
# - использование сокетов для работы по TCP.

import dis

class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        # К моменту начала работы метода __init__ метакласса
        # словарь атрибутов контролируемого класса уже сформирован.
        for key, value in clsdict.items():
            # Пропустить специальные и частные методы
            #if key.startswith("__"): continue

            # Пропустить любые невызываемые объекты
            if not hasattr(value, "__call__"): continue

            if key == "__init__":
                # Проверить наличие строки listen
                if not self.dis_func(value, 'listen'):
                    raise TypeError("Метод %s должен иметь вызов listen" % key)

            if key == "main":
                # Проверить наличие строки accept
                if not self.dis_func(value, 'accept'):
                    raise TypeError("Метод %s должен иметь вызов accept" % key)


        type.__init__(self, clsname, bases, clsdict)

    def dis_func(self, func, value):
        bytecode = dis.Bytecode(func)
        for instr in bytecode:
            if instr.argval == value:
                #print(instr)
                return True
        return False

class ServerVerifierBase(metaclass=ServerVerifier):
    '''
        Базовый класс. Можно оставить пустым.
    '''
    pass