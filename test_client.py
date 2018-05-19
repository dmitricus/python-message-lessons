import time
import json
from pytest import raises
import socket
from client import create_presence, translate_response, create_message
from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError


# МОДУЛЬНЫЕ ТЕСТЫ
def test_create_presence():
    # без параметров
    message = create_presence()
    assert message['action'] == "presence"
    # берем разницу во времени
    assert abs(message['time'] - time.time()) < 0.1
    assert message["user"]["account_name"] == 'Guest'
    # с именем
    message = create_presence('test_user_name')
    assert message["user"]["account_name"] == 'test_user_name'
    # неверный тип
    with raises(TypeError):
        create_presence(200)
    with raises(TypeError):
        create_presence(None)
    # Имя пользователя слишком длинное
    with raises(UsernameToLongError):
        create_presence('11111111111111111111111111')


def test_translate_message():
    # неправильный тип
    with raises(TypeError):
        translate_response(100)
    # неверная длина кода ответа
    with raises(ResponseCodeLenError):
        translate_response({'response': '5'})
    # нету ключа response
    with raises(MandatoryKeyError):
        translate_response({'one': 'two'})
    # неверный код ответа
    with raises(ResponseCodeError):
        translate_response({'response': 700})
    # все правильно
    assert translate_response({'response': 200}) == {'response': 200}


def test_create_message():
    msg = create_message('to', 'hello', 'from')
    assert msg['action'] == 'msg'
    # берем разницу во времени
    assert abs(msg['time'] - time.time()) < 0.1
    assert msg['to'] == 'to'
    assert msg['from'] == 'from'
    assert msg['message'] == 'hello'



