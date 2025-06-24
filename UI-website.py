from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib # Para hashing de contraseñas (¡usar bcrypt o Argon2 en producción real!)

app = Flask(__name__)
app.secret_key = 'your_secret_key_for_flash_messages' # Necesario para usar flash messages, ¡cambia esto en producción!

# --- Clase UserManager (Adaptada para web, sin messageboxes y con ID de retorno) ---
class UserManager:
    def __init__(self):
        self.users = []
        self.next_id = 1
        self._add_sample_users()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _add_sample_users(self):
        # El parámetro 'silent=True' ya no es necesario aquí.
        # En una app web, las respuestas se manejan con flash messages o redirecciones.
        self.create_user("admin", "admin123", "Administrador", "admin@example.com", roles=["admin", "editor"])
        self.create_user("juanp", "pass4juan", "Juan Pérez", "juan@example.com", roles=["viewer"])
        self.create_user("mariaf", "segura789", "María Fernández", "maria@example.com", roles=["editor"])

    def create_user(self, username, password, full_name, email, roles=None):
        if self.get_user_by_username(username):
            return None # Retorna None si el usuario ya existe

        hashed_password = self._hash_password(password)
        new_user = {
            "id": self.next_id,
            "username": username,
            "password_hash": hashed_password,
            "full_name": full_name,
            "email": email,
            "roles": roles if roles is not None else ["viewer"]
        }
        self.users.append(new_user)
        self.next_id += 1
        return new_user["id"] # Retorna el ID del nuevo usuario

    def get_user_by_id(self, user_id):
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None

    def get_user_by_username(self, username):
        for user in self.users:
            if user["username"] == username:
                return user
        return None

    def get_all_users_safe(self):
        """Retorna una lista de usuarios sin el hash de la contraseña."""
        safe_users = []
        for user in self.users:
            safe_user = user.copy()
            safe_user.pop("password_hash", None)
            safe_users.append(safe_user)
        return safe_users

    def update_user(self, user_id, new_full_name=None, new_email=None, new_password=None, new_roles=None):
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        if new_full_name:
            user["full_name"] = new_full_name
        if new_email:
            user["email"] = new_email
        if new_password:
            user["password_hash"] = self._hash_password(new_password)
        if new_roles is not None:
            user["roles"] = new_roles
        
        return True

    def delete_user(self, user_id):
        initial_count = len(self.users)
        self.users = [user for user in self.users if user["id"] != user_id]
        return len(self.users) < initial_count

    def authenticate_user(self, username, password):
        user = self.get_user_by_username(username)
        if user and user["password_hash"] == self._hash_password(password):
            return user
        return None

# Instancia global del gestor de usuarios
user_manager = UserManager()

# --- Rutas de Flask ---

@app.route('/')
def index():
    # Muestra la lista de usuarios y el formulario para crear uno nuevo
    users = user_manager.get_all_users_safe()
    return render_template('index.html', users=users)

@app.route('/create', methods=['POST'])
def create_user_web():
    username = request.form['username']
    password = request.form['password']
    full_name = request.form['full_name']
    email = request.form['email']
    roles_str = request.form['roles']
    roles = [r.strip() for r in roles_str.split(',')] if roles_str else ['viewer']

    if not username or not password or not full_name or not email:
        flash('Todos los campos son obligatorios (excepto roles).', 'warning')
        return redirect(url_for('index'))

    user_id = user_manager.create_user(username, password, full_name, email, roles)
    if user_id:
        flash(f'Usuario "{username}" creado con éxito. ID: {user_id}', 'success')
    else:
        flash(f'Error: El nombre de usuario "{username}" ya existe.', 'danger')
    return redirect(url_for('index'))

@app.route('/edit/<int:user_id>')
def edit_user(user_id):
    user = user_manager.get_user_by_id(user_id)
    if user:
        # Asegúrate de no enviar el hash de la contraseña a la plantilla
        safe_user = user.copy()
        safe_user.pop("password_hash", None)
        return render_template('edit_user.html', user=safe_user)
    else:
        flash(f'Usuario con ID {user_id} no encontrado.', 'danger')
        return redirect(url_for('index'))

@app.route('/update/<int:user_id>', methods=['POST'])
def update_user_web(user_id):
    new_full_name = request.form['full_name']
    new_email = request.form['email']
    new_password = request.form['password']
    new_roles_str = request.form['roles']
    new_roles = [r.strip() for r in new_roles_str.split(',')] if new_roles_str else []

    success = user_manager.update_user(
        user_id,
        new_full_name if new_full_name else None,
        new_email if new_email else None,
        new_password if new_password else None,
        new_roles
    )
    if success:
        flash(f'Usuario con ID {user_id} actualizado con éxito.', 'success')
    else:
        flash(f'Error al actualizar usuario con ID {user_id}.', 'danger')
    return redirect(url_for('index'))


@app.route('/delete/<int:user_id>')
def delete_user_web(user_id):
    success = user_manager.delete_user(user_id)
    if success:
        flash(f'Usuario con ID {user_id} eliminado con éxito.', 'success')
    else:
        flash(f'Error al eliminar usuario con ID {user_id}.', 'danger')
    return redirect(url_for('index'))

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate_user_web():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        authenticated_user = user_manager.authenticate_user(username, password)
        if authenticated_user:
            flash(f'Autenticación exitosa para "{username}". Bienvenido, {authenticated_user["full_name"]}.', 'success')
        else:
            flash(f'Error de autenticación para "{username}". Credenciales incorrectas.', 'danger')
        return redirect(url_for('index'))
    return render_template('authenticate.html') # Renderiza un formulario de login

if __name__ == '__main__':
    app.run(debug=True) # debug=True recarga el servidor automáticamente con los cambios