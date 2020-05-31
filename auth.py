from functools import wraps

from flask import render_template, request, redirect
from flask_login import login_user, logout_user, current_user

from app import app, session, login
from model import User


@login.user_loader
def load_user(user_email):
    return session.query(User).filter(User.email == user_email).first()


@app.route('/login', methods=['GET', 'POST'])
def login_handler():
    if request.method == 'GET':
        return render_template('login_page.html', msg='')

    email, password = request.form['email'], request.form['password']
    user = session.query(User).filter(User.email == email).first()
    if not user or user.password_hash != password:
        return render_template('login_page.html', msg='Неправильна пошта або пароль')
    if not user.is_active:
        return render_template('login_page.html', msg='Ваш акаунт деактивовано')
    login_user(user, remember=email)
    if user.role == 'admin':
        return redirect('/holder')
    return redirect('/apostile')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


def user_is_logged():
    return hasattr(current_user, 'email')


def user_name():
    if user_is_logged():
        return current_user.name
    return ''


def user_menu():
    if not user_is_logged():
        return [], []
    if current_user.role == 'admin':
        return [('Держателі', '/holder')]
    if current_user.role == 'holder':
        return [('Апостилі', '/apostile'), ('Довірені особи', '/trusted')]


def user_config():
    return {'logged': user_is_logged(), 'username': user_name(), 'menu': user_menu(),
            'role': current_user.role if user_is_logged() else ''}


def allowed_roles(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not user_is_logged() or current_user.role not in roles:
                return render_template('message.html', title='Посилка доступу',
                                       msg=f'В доступі відмовлено', **user_config())
            print(current_user.is_active)
            if not current_user.is_active:
                return render_template('login_page.html', msg='Ваш акаунт деактивовано')

            return func(*args, **kwargs)

        return wrapper

    return decorator
