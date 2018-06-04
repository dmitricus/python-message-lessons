import time

from pytest import raises

from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError
from client import Client


class TestClient(Client):
    # МОДУЛЬНЫЕ ТЕСТЫ
    def test_create_presence(self):
        # без параметров
        message = self.create_presence()
        assert message['action'] == "presence"
        # берем разницу во времени
        assert abs(message['time'] - time.time()) < 0.1
        assert message["user"]["account_name"] == 'Guest'
        # с именем
        message = self.create_presence('test_user_name')
        assert message["user"]["account_name"] == 'test_user_name'
        # неверный тип
        with raises(TypeError):
            self.create_presence(200)
        with raises(TypeError):
            self.create_presence(None)
        # Имя пользователя слишком длинное
        with raises(UsernameToLongError):
            self.create_presence('11111111111111111111111111')


    def test_translate_message(self):
        # неправильный тип
        with raises(TypeError):
            self.translate_response(100)
        # неверная длина кода ответа
        with raises(ResponseCodeLenError):
            self.translate_response({'response': '5'})
        # нету ключа response
        with raises(MandatoryKeyError):
            self.translate_response({'one': 'two'})
        # неверный код ответа
        with raises(ResponseCodeError):
            self.translate_response({'response': 700})
        # все правильно
        assert self.translate_response({'response': 200}) == {'response': 200}


    def test_create_message(self):
        msg = self.create_message('to', 'hello', 'from')
        assert msg['action'] == 'msg'
        # берем разницу во времени
        assert abs(msg['time'] - time.time()) < 0.1
        assert msg['to'] == 'to'
        assert msg['from'] == 'from'
        assert msg['message'] == 'hello'



