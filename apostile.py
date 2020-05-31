from math import ceil

from flask import render_template, request, redirect
from sqlalchemy import and_

from app import app, session
from auth import user_config, user_is_logged, allowed_roles
from model import Apostile, Document, TrustedInstitution, TrustedPerson


@app.route('/')
def index():
    return render_template('index.html', title='Пошук апостилів', **user_config())


@app.route('/apostile_search', methods=['POST'])
def search():
    id_, date_ = request.form['id'], request.form['date']
    if user_is_logged():
        cond = and_(Apostile.number == id_, Apostile.date == date_)
    else:
        cond = and_(Apostile.number == id_, Apostile.date == date_, Apostile.is_archived == False)
    apostile = session.query(Apostile).filter(cond).first()
    if apostile:
        return redirect(f'/apostile/{apostile.id}')
    return render_template('message.html', title='Не знайдено',
                           msg=f'Апостиль №{id_} від {date_} не знайдено',
                           **user_config())


@app.route('/apostile/<int:apostile_id>')
def get(apostile_id):
    apostile = session.query(Apostile).filter(Apostile.id == apostile_id).first()
    if not user_is_logged() and apostile.is_archived:
        return render_template('message.html', title='Не знайдено',
                               msg=f'Апостиль не знайдено', **user_config())

    document = session.query(Document).filter(Document.id == apostile.document_id).first()
    TrustedClass = TrustedInstitution if apostile.trusted_type == 'institution' else TrustedPerson
    trusted = session.query(TrustedClass).filter(TrustedClass.id == apostile.trusted_id).first().info()

    return render_template('apostile.html', title='Знайдено апостиль', **user_config(),
                           doc=document, ap=apostile, tr=trusted)


@app.route('/apostile/<int:apostile_id>/change', methods=['POST'])
@allowed_roles(['holder'])
def archive(apostile_id):
    apostile = session.query(Apostile).filter(Apostile.id == apostile_id).first()
    apostile.is_archived = not apostile.is_archived
    session.commit()
    return redirect(f'/apostile/{apostile_id}')


@app.route('/apostile')
@allowed_roles(['holder'])
def list_all():
    per_page = 10
    page = int(request.args.get('page', 1))
    query = request.args.get('search', '').lower()
    apostiles = [a for a in session.query(Apostile).all() if query in str(a.number) or
                 (query in query in 'доступний' and not a.is_archived) or
                 (query in query in 'заархівований' and a.is_archived)]
    return render_template('apostiles.html', title='Апостилі', **user_config(), s=query, aps=apostiles[
                                                                                             per_page * (
                                                                                                     page - 1):per_page * page],
                           pages=[page, ceil(len(apostiles) / per_page)])


@app.route('/apostile/search', methods=['POST'])
@allowed_roles(['holder'])
def search_post():
    query = request.form.get('query')
    return redirect(f'/apostile?search={query}')


@app.route('/apostile/create')
@allowed_roles(['holder'])
def apostile_create():
    trs = list(session.query(TrustedInstitution).filter(TrustedInstitution.is_archived == False).all()) + \
          list(session.query(TrustedPerson).filter(TrustedPerson.is_archived == False).all())
    trs = sorted([tr.short() for tr in trs])
    return render_template('create_apostile.html', title='Сворення апостилю', **user_config(), trs=trs)


def find_trusted_by_str(data):
    key = data.split('(')[0].strip()
    if '(особа)' in data:
        obj_id = session.query(TrustedPerson).filter(TrustedPerson.person_name == key).first().id
        obj_type = 'person'
    else:
        obj_id = session.query(TrustedInstitution).filter(TrustedInstitution.institution_name == key).first().id
        obj_type = 'institution'
    return obj_id, obj_type


@app.route('/apostile/create', methods=['POST'])
@allowed_roles(['holder'])
def apostile_create_post():
    count = session.query(Apostile).filter(Apostile.number == int(request.form['number'])).count()
    if count:
        return render_template('message.html', title='Помилка',
                               msg=f'Апостиль з номером {request.form["number"]} уже існує', **user_config())

    doc = Document(
        country=request.form['country'],
        date=request.form['doc_date'],
        author_name=request.form['person_name'],
        author_info=request.form['person_position'],
        stamp_info=request.form['stamp_info'] if request.form['stamp_info'] else '-/-/-'
    )
    session.add(doc)
    session.flush()

    tr_id, tr_type = find_trusted_by_str(request.form['ap_author'])
    ap = Apostile(
        number=int(request.form['number']),
        date=request.form['ap_date'],
        is_archived=False,
        trusted_id=tr_id, trusted_type=tr_type,
        document_id=doc.id
    )
    session.add(ap)
    session.flush()
    session.commit()

    return redirect(f'/apostile/{ap.id}')
