# метакласс ClientVerifier, выполняющий базовую проверку класса Клиент (для некоторых проверок уместно использовать модуль dis)
# - отсутствие вызовов accept и listen для сокетов
# - использование сокетов для работы по TCP
# - отсутствие создания сокетов на уровне классов, т.е. отсутствие конструкций вида:
# class Client:
#    s = socket()
#    ...
import dis

class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        # К моменту начала работы метода __init__ метакласса
        # словарь атрибутов контролируемого класса уже сформирован.
        for key, value in clsdict.items():
            # Пропустить специальные и частные методы
            #if key.startswith("__"): continue

            # Пропустить любые невызываемые объекты
            if not hasattr(value, "__call__"): continue

            if key == "__init__":
                # Проверить наличие строки connect
                if not self.dis_func(value, 'connect'):
                    raise TypeError("Метод %s должен иметь вызов connect" % key)


        type.__init__(self, clsname, bases, clsdict)

    def dis_func(self, func, value):
        bytecode = dis.Bytecode(func)
        for instr in bytecode:
            if instr.argval == value:
                #print(instr)
                return True
        return False

class ClientVerifierBase(metaclass=ClientVerifier):
    '''
        Базовый класс. Можно оставить пустым.
    '''
    pass
