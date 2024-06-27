from flask import session, redirect
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'steam64id' not in session:
            return redirect('/', 302)
        return f(*args, **kwargs)
    return decorated_function
