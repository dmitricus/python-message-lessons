from db.server_controller import Storage

def login_required(session, login):
    def decorator(func):
        def wrapper(*args, **kwargs):
            storage = Storage(session)
            user = storage.select_user(login)
            if user.is_authenticated and user.is_active:
                print("Пользователь {} авторизован".format(user.Name))
            else:
                print("Пользователь {} не авторизован".format(user.Name))
                result = func(*args, **kwargs)
                return result

        return wrapper

    return decorator