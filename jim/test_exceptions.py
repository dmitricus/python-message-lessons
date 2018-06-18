from .exceptions import WrongParamsError, ToLongError, WrongActionError, WrongDictError, ResponseCodeError


def test_str():
    wrong_dict = {'test': 'test', 'other': 'other'}

    e = WrongParamsError(wrong_dict)
    assert str(e) == "Wrong action params: {'test': 'test', 'other': 'other'}"
    e = ToLongError('field_name', 30, 25)
    assert str(e) == "field_name: 30 to long (> 25 simbols)"
    e = WrongActionError('test_action')
    assert str(e) == "Wrong action: test_action"
    e = WrongDictError(wrong_dict)
    assert str(e) == "Wrong input dict: {'test': 'test', 'other': 'other'}"
    e = ResponseCodeError(666)
    assert str(e) == "Wrong response code: 666"
