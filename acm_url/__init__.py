import os
from flask import Flask, render_template, request, url_for, redirect, session
from acm_url.db import get_db
import string
import secrets
import re
from acm_url.forms import CreateForm, PasswordForm
from werkzeug.security import check_password_hash
from datetime import timedelta

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.permanent_session_lifetime = timedelta(minutes=30)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev', 
        DATABASE=os.environ.get('DATABASE_URL') or os.path.join(app.instance_path, 'acm_url.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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

            db = get_db()

            if not vanity:
                vanity = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(10))
                old_entry = db.execute(
                    'SELECT vanity, url'
                    ' FROM urls WHERE LOWER(vanity) = LOWER(?)',
                    (vanity,)
                ).fetchone()

                while old_entry is not None:
                    vanity = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(12))
                    old_entry = db.execute(
                        'SELECT vanity, url'
                        ' FROM urls WHERE LOWER(vanity) = LOWER(?)',
                        (vanity,)
                    ).fetchone()
            else:
                if vanity.lower() == 'create':
                    return render_template('url.html', form=create_form, error="You cannot use this short name. Please try again.")
                old_entry = db.execute(
                    'SELECT vanity, url'
                    ' FROM urls WHERE LOWER(vanity) = LOWER(?)',
                    (vanity,)
                ).fetchone()
                if old_entry is not None:
                    return render_template('url.html', form=create_form, error="Short name already taken! Please try again.")
            
            db.execute(
                'INSERT INTO urls (vanity, url)'
                ' VALUES (?, ?)',
                (vanity, url)
            )
            db.commit()
            return render_template('success.html', url=request.url_root + vanity)

        return render_template('url.html', form=create_form)

    @app.route('/<vanity>')
    def vanity(vanity):
        db = get_db()
        url = db.execute(
            'SELECT url, visit_count'
            ' FROM urls WHERE LOWER(vanity) = LOWER(?)',
            (vanity,)
        ).fetchone()

        if url is None:
            return render_template('404.html')
    
        db.execute(
            'UPDATE urls SET visit_count = ?'
            ' WHERE LOWER(vanity) = LOWER(?)',
            (url['visit_count'] + 1, vanity)
        )
        db.commit()
        # return redirect
        return redirect(url['url'], code=302)

    from . import db
    db.init_app(app)

    return app