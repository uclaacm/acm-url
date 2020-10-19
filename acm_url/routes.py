from flask import Flask, render_template, request, url_for, redirect, session
from acm_url import app, db
import string
import secrets
import re
import os
from acm_url.forms import CreateForm, PasswordForm
from werkzeug.security import check_password_hash
from acm_url.schema import Url
from sqlalchemy import func

@app.route('/', methods=('GET', 'POST'))
def index():
    user_id = session.get('user_id')

    if user_id is None:
        password_form = PasswordForm()            
        if password_form.validate_on_submit():
            pwd = password_form.password.data or ""
            if check_password_hash(os.environ.get('OFFICER_PWD'), pwd):
                session.clear()
                session.permanent = True
                session['user_id'] = ''.join(secrets.choice(string.digits) for i in range(5))
                return redirect(url_for('create'))
            else:
                session.clear()
                return render_template('password.html', form=password_form, error="Incorrect")
        else:
            return render_template('password.html', form=password_form)
            
    return redirect(url_for('create'))

@app.route('/create', methods=('GET', 'POST'))
def create():
    if session.get('user_id') is None:
        return redirect(url_for('index'))
    
    create_form = CreateForm()

    if create_form.validate_on_submit():
        vanity = create_form.vanity.data
        url = create_form.url.data

        if not(url.startswith('http://') or url.startswith('https://')):
            url = 'https://' + url

        if not vanity:
            vanity = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(10))
            old_entry = Url.query.filter(func.lower(Url.vanity) == func.lower(vanity)).first()

            while old_entry is not None:
                vanity = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(12))
                old_entry = Url.query.filter(func.lower(Url.vanity) == func.lower(vanity)).first()
        else:
            if vanity.lower() == 'create':
                return render_template('url.html', form=create_form, error="You cannot use this short name. Please try again.")
            
            old_entry = Url.query.filter(func.lower(Url.vanity) == func.lower(vanity)).first()
            
            if old_entry is not None:
                return render_template('url.html', form=create_form, error="Short name already taken! Please try again.")
        
        new_url = Url(vanity=vanity, url=url)
        db.session.add(new_url)
        db.session.commit()
        return render_template('success.html', url=request.url_root + vanity)

    return render_template('url.html', form=create_form)

@app.route('/<vanity>')
def vanity(vanity):
    entry = Url.query.filter(func.lower(Url.vanity) == func.lower(vanity)).first()

    if entry is None:
        return render_template('404.html')

    entry.visit_count = entry.visit_count + 1
    db.session.commit()

    # return redirect
    return redirect(entry.url, code=302)
