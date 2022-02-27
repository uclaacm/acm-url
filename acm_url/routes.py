from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session
from acm_url import app, db
import string
import secrets
import re
import os
from acm_url.forms import CreateForm, PasswordForm, EditForm
from werkzeug.security import check_password_hash
from acm_url.schema import URL
from sqlalchemy import func

def is_unavaliable(vanity):
    return vanity.lower() in ['create', 'edit', 'delete', 'all', 'login', 'logout']

# Default endpoint. If logged in, redirect to create. Otherwise, prompt them for password. 
# If correct, redirect to create, otherwise, stay here.
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

# Endpoint for creating a new vanity url. GET request returns the form.
# POST request validates and creates the new url in the DB. 
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
            old_entry = URL.query.filter(func.lower(URL.vanity) == func.lower(vanity)).first()

            while old_entry is not None:
                vanity = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(12))
                old_entry = URL.query.filter(func.lower(URL.vanity) == func.lower(vanity)).first()
        else:
            if is_unavaliable(vanity):
                return render_template('url.html', form=create_form, error="You cannot use this short name. Please try again.")
            
            old_entry = URL.query.filter(func.lower(URL.vanity) == func.lower(vanity)).first()
            
            if old_entry is not None:
                return render_template('url.html', form=create_form, error="Short name already taken! Please try again.")
        
        new_url = URL(vanity=vanity, url=url)
        db.session.add(new_url)
        db.session.commit()
        return render_template('success.html', url=request.url_root + vanity)

    return render_template('url.html', form=create_form)

# Endpoint for accessing a vanity url. A simple redirect to the URL on file.
@app.route('/<vanity>')
def vanity(vanity):
    entry = URL.query.filter(func.lower(URL.vanity) == func.lower(vanity)).first()

    if entry is None:
        return render_template('404.html')

    entry.last_visited = datetime.timestamp(datetime.now())
    entry.visit_count = entry.visit_count + 1
    db.session.commit()
    
    # return redirect
    return redirect(entry.url, code=302)

@app.route('/all', methods=('GET', 'POST'))
def all():
    page = request.args.get('page', 1, type=int)
    links = URL.query.order_by(URL.visit_count.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('all', page=links.next_num) if links.has_next else None
    prev_url = url_for('all', page=links.prev_num) if links.has_prev else None
    return render_template('links.html', links=links.items,next_url=next_url, prev_url=prev_url)

# Endpoint for deleting a vanity url.
@app.route('/delete/<vanity>', methods=['POST'])
def delete(vanity):
    entry = URL.query.filter(func.lower(URL.vanity) == func.lower(vanity)).first()

    # Check if the vanity is valid
    if is_unavaliable(vanity):
        return f"You cannot delete the short name {vanity}", 405

    if entry is None:
        return render_template('404.html')

    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('all'))

@app.route('/edit', methods=['GET','POST'])
def edit():
    args = request.args
    vanity = args.get("vanity")

    # Check if the vanity is valid
    if vanity is None or is_unavaliable(vanity):
        return render_template("404.html")
    # Check if vanity exists
    entry = URL.query.filter(func.lower(URL.vanity) == func.lower(vanity)).first()
    if entry is None:
        return render_template('404.html')

    edit_form = EditForm()
    if edit_form.validate_on_submit():
        url = edit_form.url.data

        # Update database
        if not(url.startswith('http://') or url.startswith('https://')):
            url = 'https://' + url
        entry.url = url
        db.session.commit()
        return redirect(url_for('all'))

    return render_template('edit.html', form=edit_form, vanity=vanity, url=entry.url)


@app.route('/admin', methods=('GET', 'POST'))
def admin():
    if session.get('user_id') is None:
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    links = URL.query.order_by(URL.visit_count.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('all', page=links.next_num) if links.has_next else None
    prev_url = url_for('all', page=links.prev_num) if links.has_prev else None
    return render_template('admin.html', links=links.items,next_url=next_url, prev_url=prev_url)
    

