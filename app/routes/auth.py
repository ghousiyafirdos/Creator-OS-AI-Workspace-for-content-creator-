from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new CreatorOS account without email verification."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        full_name = form.full_name.data.strip()

        user = User.query.filter_by(email=email).first()
        if user:
            user.full_name = full_name
            user.set_password(form.password.data)
            user.is_verified = True
        else:
            user = User(
                full_name=full_name,
                email=email,
                is_verified=True
            )
            user.set_password(form.password.data)
            db.session.add(user)

        db.session.commit()
        login_user(user)
        flash("Account created successfully. Welcome to your CreatorOS Workspace.", "success")
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Sign in with email and password only."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            user.is_verified = True
            db.session.commit()
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash("Invalid email address or password. Please try again.", "danger")

    return render_template('auth/login.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Start password reset without email verification."""
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No registered account found with that email address.", "danger")
            return render_template('auth/forgot_password.html', form=form)

        return redirect(url_for('auth.reset_password', email=email))

    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset a password directly without email verification."""
    email = request.args.get('email', '').lower().strip() or request.form.get('email', '').lower().strip()
    user = User.query.filter_by(email=email).first() if email else None

    if not user:
        flash("Enter a registered account email to reset the password.", "warning")
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password updated successfully. Please sign in with your new credentials.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form, email=email)


@auth_bp.route('/logout')
@login_required
def logout():
    """User Logout Route."""
    logout_user()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('auth.login'))
