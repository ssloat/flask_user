from mysite import app, db
from mysite.user.models import User, ProviderId

from flask import render_template, redirect, url_for 
from flask.ext.login import login_user, logout_user, current_user

from oauth import OAuthSignIn


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    social_id, name, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email)
        provider_id = ProviderId(id=social_id, user=user)
        db.session.add(user)
        db.session.add(provider_id)
        db.session.commit()

    login_user(user, True)
    return redirect(url_for('index'))


