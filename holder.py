import datetime
from math import ceil

from flask import render_template, request, redirect

from app import app, session

from auth import user_config, allowed_roles
from model import User


@app.route('/holder')
@allowed_roles(['admin'])
def get_all_holders():
    per_page = 5
    page = int(request.args.get('page', 1))
    query = request.args.get('search', '').lower()

    holders = session.query(User).filter(User.role == 'holder').all()
    holders = [h for h in holders if query in h.name.lower() or query in h.email.lower()]
    holders = sorted(holders, key=lambda h: h.name)
    return render_template('holders.html', title='Держателі', **user_config(), s=query, holders=holders[
                                                                                                per_page * (
                                                                                                        page - 1):per_page * page],
                           pages=[page, ceil(len(holders) / per_page)], url=request.url)


@app.route('/holder/search', methods=['POST'])
@allowed_roles(['admin'])
def search_post_holder():
    query = request.form.get('query')
    return redirect(f'/holder?search={query}')


@app.route('/holder/update/<int:obj_id>', methods=['POST'])
@allowed_roles(['admin'])
def update_holder(obj_id):
    obj = session.query(User).filter(User.id == obj_id).first()
    obj.is_active = not obj.is_active
    session.commit()
    return redirect(request.args['url'])


@app.route('/holder/create')
@allowed_roles(['admin'])
def create_holder():
    return render_template('create_holder.html', title='Новий держатель', **user_config())


@app.route('/holder/create', methods=['POST'])
@allowed_roles(['admin'])
def create_holder_post():
    count = session.query(User).filter(User.email == request.form['email']).count()
    if count:
        return render_template('message.html', title='Помилка',
                               msg=f'Користувач з поштою {request.form["email"]} уже існує', **user_config())

    holder = User(
        email=request.form['email'],
        name=request.form['name'],
        password_hash=request.form['pass'],
        role='holder',
        is_active=True,
        created_at=datetime.date.today()
    )
    session.add(holder)
    session.commit()
    return redirect('/holder')


@app.route('/holder/edit/<int:h_id>')
@allowed_roles(['admin'])
def edit_holder(h_id):
    holder = session.query(User).filter(User.id == h_id).first()
    return render_template('update_holder.html', title='Редагування держателя', **user_config(), h=holder,
                           redirect=request.args['redirect'])


@app.route('/holder/edit/<int:h_id>', methods=['POST'])
@allowed_roles(['admin'])
def edit_holder_post(h_id):
    holder = session.query(User).filter(User.id == h_id).first()
    holder.name = request.form['name']
    holder.email = request.form['email']
    if request.form['pass']:
        holder.password_hash = request.form['pass']
    session.commit()
    return redirect(request.args['redirect'])
