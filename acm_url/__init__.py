import os
from flask import Flask, render_template, request, url_for, redirect
from acm_url.db import get_db
import string
import secrets
import re
from acm_url.forms import CreateForm

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # TODO: replace secret key before deploy
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev', 
        DATABASE=os.path.join(app.instance_path, 'acm_url.sqlite'),
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
    def create():
        # ask for secret password

        create_form = CreateForm()

        if create_form.validate_on_submit():
            vanity = create_form.vanity.data
            url = create_form.url.data

            db = get_db()

            if not vanity:
                vanity = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(10))
                old_entry = db.execute(
                    'SELECT vanity, url'
                    ' FROM urls WHERE vanity = ?',
                    (vanity,)
                ).fetchone()

                while old_entry is not None:
                    vanity = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(12))
                    old_entry = db.execute(
                        'SELECT vanity, url'
                        ' FROM urls WHERE vanity = ?',
                        (vanity,)
                    ).fetchone()
            else:                
                old_entry = db.execute(
                    'SELECT vanity, url'
                    ' FROM urls WHERE vanity = ?',
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
            ' FROM urls WHERE vanity = ?',
            (vanity,)
        ).fetchone()

        if url is None:
            return render_template('404.html')
    
        db.execute(
            'UPDATE urls SET visit_count = ?'
            ' WHERE vanity = ?',
            (url['visit_count'] + 1, vanity)
        )
        db.commit()
        # return redirect
        return redirect(url['url'], code=302)

    from . import db
    db.init_app(app)

    return app