from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from .models import db, User, Role
from .forms import LoginForm, UserForm, EditUserForm, ChangePasswordForm

views = Blueprint('views', __name__)

@views.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@views.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('views.index')
            return redirect(next_page)
        flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html', form=form)

@views.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('views.index'))

@views.route('/user/<int:id>')
def user_view(id):
    user = User.query.get_or_404(id)
    return render_template('user_view.html', user=user)

@views.route('/user/create', methods=['GET', 'POST'])
@login_required
def user_create():
    form = UserForm()
    if form.validate_on_submit():
        # Проверяем, существует ли пользователь с таким логином
        if User.query.filter_by(username=form.username.data).first():
            flash('Пользователь с таким логином уже существует')
            return render_template('user_create.html', form=form)
        
        user = User(
            username=form.username.data,
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            role_id=form.role.data if form.role.data != 0 else None
        )
        user.password = form.password.data
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Пользователь успешно создан')
            return redirect(url_for('views.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании пользователя: {str(e)}')
    
    return render_template('user_create.html', form=form)

@views.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit(id):
    user = User.query.get_or_404(id)
    form = EditUserForm()
    
    if request.method == 'GET':
        form.last_name.data = user.last_name
        form.first_name.data = user.first_name
        form.middle_name.data = user.middle_name
        form.role.data = user.role_id or 0
    
    if form.validate_on_submit():
        user.last_name = form.last_name.data
        user.first_name = form.first_name.data
        user.middle_name = form.middle_name.data
        user.role_id = form.role.data if form.role.data != 0 else None
        
        try:
            db.session.commit()
            flash('Пользователь успешно обновлен')
            return redirect(url_for('views.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении пользователя: {str(e)}')
    
    return render_template('user_edit.html', form=form, user=user)

@views.route('/user/delete/<int:id>', methods=['POST'])
@login_required
def user_delete(id):
    user = User.query.get_or_404(id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удален')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пользователя: {str(e)}')
    
    return redirect(url_for('views.index'))

@views.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Проверяем старый пароль
        if not current_user.verify_password(form.old_password.data):
            flash('Старый пароль введен неверно')
            return render_template('change_password.html', form=form)
        
        current_user.password = form.new_password.data
        
        try:
            db.session.commit()
            flash('Пароль успешно изменен')
            return redirect(url_for('views.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при изменении пароля: {str(e)}')
    
    return render_template('change_password.html', form=form)
