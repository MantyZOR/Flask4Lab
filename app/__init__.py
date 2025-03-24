# _init_.py
from flask import Flask
from flask_login import LoginManager
from .models import db, User, Role
from .config import Config

login_manager = LoginManager()
login_manager.login_view = 'views.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # Регистрация представлений
    from .views import views
    app.register_blueprint(views)
    
    # Создание таблиц в базе данных и начальные данные
    with app.app_context():
        db.create_all()
        
        # Создание ролей, если их нет
        from .models import Role
        if not Role.query.first():
            roles = [
                {'name': 'Admin', 'description': 'Administrator with full access'},
                {'name': 'User', 'description': 'Regular user with limited access'}
            ]
            for role_data in roles:
                role = Role(**role_data)
                db.session.add(role)
            db.session.commit()
            
            # Создание первого пользователя-администратора
            if not User.query.first():
                admin_role = Role.query.filter_by(name='Admin').first()
                admin_user = User(
                    username='admin',
                    first_name='Администратор',
                    last_name='Системы',
                    role=admin_role
                )
                admin_user.password = 'Admin123!'  # Используется сеттер для хеширования
                db.session.add(admin_user)
                db.session.commit()
                print('Создан пользователь-администратор:')
                print('Логин: admin')
                print('Пароль: Admin123!')
    
    return app
