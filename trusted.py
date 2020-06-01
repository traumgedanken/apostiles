from math import ceil

from flask import render_template, request, redirect
from cloudinary.uploader import upload

from app import app, session
from auth import allowed_roles, user_config
from model import TrustedPerson, TrustedInstitution


@app.route('/trusted/create_person', methods=['GET'])
@allowed_roles(['holder', 'admin'])
def create_person():
    return render_template('create_trusted_person.html', title='Нова довірена особа', **user_config())


def load_image(file):
    response = upload(file, api_key='929139732589989', api_secret='Af4pY6zl9IbuLLZzVrICvmZ51HM', cloud_name='progout')
    return response['url']


@app.route('/trusted/create_person', methods=['POST'])
@allowed_roles(['holder', 'admin'])
def create_person_post():
    sign_url = load_image(request.files['sign_image'])
    person = TrustedPerson(
        person_name=request.form['name'],
        location=request.form['location'],
        licence_number=request.form['license'],
        stamp_info=request.form['stamp_info'] if request.form['stamp_info'] else '-/-/-',
        sign_image_url=sign_url
    )
    session.add(person)
    session.commit()
    return redirect(f'/trusted')


@app.route('/trusted/create_institution', methods=['GET'])
@allowed_roles(['holder', 'admin'])
def create_institution():
    return render_template('create_trusted_institution.html', title='Нова довірена особа', **user_config())


@app.route('/trusted/create_institution', methods=['POST'])
@allowed_roles(['holder', 'admin'])
def create_institution_post():
    sign_url = load_image(request.files['sign_image'])
    inst = TrustedInstitution(
        institution_name=request.form['inst_name'],
        person_name=request.form['person_name'],
        person_position=request.form['person_position'],
        location=request.form['location'],
        stamp_info=request.form['stamp_info'] if request.form['stamp_info'] else '-/-/-',
        sign_image_url=sign_url
    )
    session.add(inst)
    session.commit()
    return redirect(f'/trusted')


@app.route('/trusted')
@allowed_roles(['holder', 'admin'])
def list_all_trs():
    per_page = 5
    page = int(request.args.get('page', 1))
    query = request.args.get('search', '').lower()

    trs = list(session.query(TrustedInstitution).all()) + list(session.query(TrustedPerson).all())
    trs = [t.info() for t in trs]
    trs = [t for t in trs if query.lower() in ''.join(t.values()).lower()]
    trs = sorted(trs, key=lambda t: t['person_name'])
    return render_template('trusteds.html', title='Завірятелі', **user_config(), s=query, trs=trs[
                                                                                              per_page * (
                                                                                                          page - 1):per_page * page],
                           pages=[page, ceil(len(trs) / per_page)], url=request.url)


@app.route('/trusted/search', methods=['POST'])
@allowed_roles(['holder', 'admin'])
def search_post_trusted():
    query = request.form.get('query')
    return redirect(f'/trusted?search={query}')


@app.route('/trusted/<string:table>/change/<int:obj_id>', methods=['POST'])
@allowed_roles(['holder', 'admin'])
def update_trusted(table, obj_id):
    if table == 'person':
        obj = session.query(TrustedPerson).filter(TrustedPerson.id == obj_id).first()
    else:
        obj = session.query(TrustedInstitution).filter(TrustedInstitution.id == obj_id).first()
    obj.is_archived = not obj.is_archived
    session.commit()
    return redirect(request.args['url'])


@app.route('/trusted/<string:table>/edit/<int:tr_id>')
@allowed_roles(['holder', 'admin'])
def edit_trusted(table, tr_id):
    if table == 'person':
        tr = session.query(TrustedPerson).filter(TrustedPerson.id == tr_id).first()
        return render_template('update_trusted_person.html', title='Оновлення особи', **user_config(),
                               redirect=request.args['redirect'], tr=tr)
    else:
        tr = session.query(TrustedInstitution).filter(TrustedInstitution.id == tr_id).first()
        return render_template('update_trusted_institution.html', title='Оновлення організації', **user_config(),
                               redirect=request.args['redirect'], tr=tr)


@app.route('/trusted/<string:table>/edit/<int:tr_id>', methods=['POST'])
@allowed_roles(['holder', 'admin'])
def edit_trusted_post(table, tr_id):
    if table == 'person':
        tr = session.query(TrustedPerson).filter(TrustedPerson.id == tr_id).first()
        tr.location = request.form['location']
        tr.license_number = request.form['license']
        tr.stamp_info = request.form['stamp_info'] if request.form['stamp_info'] else '-/-/-'
        if request.files['sign_image']:
            tr.sign_image_url = load_image(request.files['sign_image'])
    else:
        tr = session.query(TrustedInstitution).filter(TrustedInstitution.id == tr_id).first()
        tr.person_name = request.form['person_name']
        tr.person_position = request.form['person_position']
        tr.location = request.form['location']
        tr.stamp_info = request.form['stamp_info'] if request.form['stamp_info'] else '-/-/-'
        if request.files['sign_image']:
            tr.sign_image_url = load_image(request.files['sign_image'])
    session.commit()
    return redirect(request.args['redirect'])
