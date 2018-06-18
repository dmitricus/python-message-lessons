import time
from pytest import raises
from .core import MaxLengthField, JimAction, JimPresence, JimMessage, ResponseField, Jim, JimResponse
from .exceptions import WrongParamsError, ToLongError, WrongActionError, WrongDictError, ResponseCodeError


class TestMaxLengthField:
    def test_set(self):
        class TestClass:
            name = MaxLengthField('name', 2)

        t1 = TestClass()
        t1.name = 'ab'
        assert t1.name == 'ab'
        with raises(ToLongError):
            t1.name = 'abc'


class TestJimAction:

    def setup(self):
        self.ja = JimAction('presence')

    def test_slots(self):
        assert self.ja.action == 'presence'
        assert abs(self.ja.time - time.time()) < 0.1
        # - если используем слоты
        # with raises(AttributeError):
        # ja.new = 123
        ja = JimAction(**{'action': 'presence'})
        assert ja.action == 'presence'
        with raises(TypeError):
            ja = JimAction(**{'action': 'presence', 'new': 123})

    def test_to_dict(self):
        ja_dict = self.ja.to_dict()
        assert ja_dict['action'] == 'presence'
        assert 'time' in ja_dict

    # def test_create_from_action(self):
    #     presence_dict = {'action': 'presence', 'account_name': 'name', 'time': time.time()}
    #     presence = JimAction.create_from_dict()


class TestJimPresence:
    def setup(self):
        self.jp = JimPresence('Test')

    def test_init(self):
        assert self.jp.action == 'presence'
        assert self.jp.account_name == 'Test'

    def test_to_dict(self):
        jp_dict = self.jp.to_dict()
        assert jp_dict['account_name'] == 'Test'
        assert 'action' in jp_dict


class TestJimMessage:
    def setup(self):
        self.jm = JimMessage(**{'to': 'test', 'from_': 'leo', 'message': 'hello'})

    def test_init(self):
        assert self.jm.action == 'msg'
        assert self.jm.to == 'test'

    def test_to_dict(self):
        j_dict = self.jm.to_dict()
        assert j_dict['to'] == 'test'
        assert j_dict['from'] == 'leo'
        assert j_dict['message'] == 'hello'
        assert 'action' in j_dict


class TestResponseField:
    def test_get_set(self):
        class MyClass:
            response = ResponseField('response')

        m = MyClass()
        m.response = 200
        assert m.response == 200
        with raises(ResponseCodeError):
            m.response = 666


class TestJimResponce:
    def test_to_dict(self):
        jr = JimResponse(200)
        j_dict = jr.to_dict()
        assert 'response' in j_dict
        assert j_dict['response'] == 200


class TestJim:

    def test_time_type(self):
        assert isinstance(time.time(), float)

    # самый важный тест создание объекта из словаря
    def test_from_dict(self):
        #presence
        presence_dict = {'action': 'presence', 'account_name': 'name', 'time': time.time()}
        presence = Jim.from_dict(presence_dict)
        assert presence.action == 'presence'
        assert presence.account_name == 'name'
        assert abs(presence.time-time.time()) < 0.1
        # message
        message_dict = {'action': 'msg', 'message': 'hello', 'to': 'to', 'from': 'from', 'time': time.time()}
        message = Jim.from_dict(message_dict)
        assert message.message == 'hello'
        assert abs(message.time - time.time()) < 0.1
        #response
        response_dict = {'response': 200}
        response = Jim.from_dict(response_dict)
        assert response.response == 200
        #исключительные ситуации
        #в словаре нету action и нету response
        error_dict = {'test': 'test'}
        with raises(WrongDictError):
            Jim.from_dict(error_dict)
        #в словаре неверное действие
        error_dict = {'action': 'test'}
        with raises(WrongActionError):
            Jim.from_dict(error_dict)
        #в словаре недостаточно параметров
        error_dict = {'action': 'msg', 'message': 'hello'}
        with raises(WrongParamsError):
            Jim.from_dict(error_dict)







