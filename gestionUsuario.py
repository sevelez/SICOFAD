import hashlib
import os

class UserManager:
    def __init__(self):
        """
        Inicializa el gestor de usuarios.
        En una aplicación real, esto cargaría los usuarios desde una base de datos.
        """
        self.users = [] # Almacena usuarios en memoria como una lista de diccionarios
        self.next_id = 1 # Para asignar IDs únicos automáticamente

        # Opcional: cargar algunos usuarios de ejemplo
        self._add_sample_users()

    def _hash_password(self, password):
        """
        Hashea la contraseña para no almacenarla en texto plano.
        En producción, usa un algoritmo más robusto como bcrypt o Argon2.
        """
        # Usamos SHA256 por simplicidad, pero no es recomendado para contraseñas de producción
        return hashlib.sha256(password.encode()).hexdigest()

    def _add_sample_users(self):
        """Añade algunos usuarios de ejemplo para probar."""
        self.create_user("admin", "admin123", "Administrador", "admin@example.com", roles=["admin", "editor"])
        self.create_user("juanp", "pass4juan", "Juan Pérez", "juan@example.com", roles=["viewer"])
        self.create_user("mariaf", "segura789", "María Fernández", "maria@example.com", roles=["editor"])


    def create_user(self, username, password, full_name, email, roles=None):
        """
        Crea un nuevo usuario y lo añade a la lista.
        :param username: Nombre de usuario único.
        :param password: Contraseña del usuario.
        :param full_name: Nombre completo del usuario.
        :param email: Correo electrónico del usuario.
        :param roles: Lista de roles asignados al usuario (ej. ["admin", "viewer"]).
        :return: El diccionario del usuario creado si tiene éxito, None si el usuario ya existe.
        """
        if self.get_user_by_username(username):
            print(f"Error: El nombre de usuario '{username}' ya existe.")
            return None

        hashed_password = self._hash_password(password)
        new_user = {
            "id": self.next_id,
            "username": username,
            "password_hash": hashed_password,
            "full_name": full_name,
            "email": email,
            "roles": roles if roles is not None else ["viewer"] # Rol por defecto
        }
        self.users.append(new_user)
        self.next_id += 1
        print(f"Usuario '{username}' creado con éxito. ID: {new_user['id']}")
        return new_user

    def get_user_by_id(self, user_id):
        """
        Busca un usuario por su ID.
        :param user_id: ID del usuario.
        :return: Diccionario del usuario si lo encuentra, None en caso contrario.
        """
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None

    def get_user_by_username(self, username):
        """
        Busca un usuario por su nombre de usuario.
        :param username: Nombre de usuario.
        :return: Diccionario del usuario si lo encuentra, None en caso contrario.
        """
        for user in self.users:
            if user["username"] == username:
                return user
        return None

    def list_users(self):
        """
        Lista todos los usuarios registrados.
        :return: Lista de diccionarios de usuarios.
        """
        if not self.users:
            print("No hay usuarios registrados.")
            return []
        print("\n--- Lista de Usuarios ---")
        for user in self.users:
            # No mostrar el hash de la contraseña directamente
            display_user = user.copy()
            display_user.pop("password_hash", None)
            print(f"ID: {display_user['id']}, Username: {display_user['username']}, Nombre: {display_user['full_name']}, Roles: {', '.join(display_user['roles'])}")
        print("-------------------------")
        return self.users

    def update_user(self, user_id, new_full_name=None, new_email=None, new_password=None, new_roles=None):
        """
        Actualiza la información de un usuario existente.
        :param user_id: ID del usuario a actualizar.
        :param new_full_name: Nuevo nombre completo (opcional).
        :param new_email: Nuevo correo electrónico (opcional).
        :param new_password: Nueva contraseña (opcional).
        :param new_roles: Nuevos roles (lista, opcional).
        :return: True si la actualización fue exitosa, False en caso contrario.
        """
        user = self.get_user_by_id(user_id)
        if not user:
            print(f"Error: Usuario con ID {user_id} no encontrado.")
            return False

        if new_full_name:
            user["full_name"] = new_full_name
        if new_email:
            user["email"] = new_email
        if new_password:
            user["password_hash"] = self._hash_password(new_password)
        if new_roles is not None:
            user["roles"] = new_roles
        
        print(f"Usuario '{user['username']}' (ID: {user_id}) actualizado con éxito.")
        return True

    def delete_user(self, user_id):
        """
        Elimina un usuario por su ID.
        :param user_id: ID del usuario a eliminar.
        :return: True si el usuario fue eliminado, False en caso contrario.
        """
        initial_count = len(self.users)
        self.users = [user for user in self.users if user["id"] != user_id]
        if len(self.users) < initial_count:
            print(f"Usuario con ID {user_id} eliminado con éxito.")
            return True
        else:
            print(f"Error: Usuario con ID {user_id} no encontrado.")
            return False

    def authenticate_user(self, username, password):
        """
        Verifica las credenciales de un usuario.
        :param username: Nombre de usuario.
        :param password: Contraseña en texto plano.
        :return: El diccionario del usuario si la autenticación es exitosa, None en caso contrario.
        """
        user = self.get_user_by_username(username)
        if user and user["password_hash"] == self._hash_password(password):
            print(f"Autenticación exitosa para '{username}'.")
            return user
        print(f"Error de autenticación para '{username}'. Credenciales incorrectas.")
        return None

# --- Función Principal para Demostración ---
def main():
    user_manager = UserManager()

    while True:
        print("\n--- Menú de Gestión de Usuarios ---")
        print("1. Crear Usuario")
        print("2. Listar Usuarios")
        print("3. Buscar Usuario por ID")
        print("4. Buscar Usuario por Username")
        print("5. Actualizar Usuario")
        print("6. Eliminar Usuario")
        print("7. Autenticar Usuario")
        print("8. Salir")

        choice = input("Ingrese su opción: ")

        if choice == '1':
            username = input("Ingrese nombre de usuario: ")
            password = input("Ingrese contraseña: ")
            full_name = input("Ingrese nombre completo: ")
            email = input("Ingrese correo electrónico: ")
            roles_str = input("Ingrese roles separados por coma (ej: admin,editor) [opcional]: ")
            roles = [role.strip() for role in roles_str.split(',')] if roles_str else None
            user_manager.create_user(username, password, full_name, email, roles)
        
        elif choice == '2':
            user_manager.list_users()

        elif choice == '3':
            try:
                user_id = int(input("Ingrese el ID del usuario a buscar: "))
                user = user_manager.get_user_by_id(user_id)
                if user:
                    # Mostrar información relevante sin el hash de contraseña
                    display_user = user.copy()
                    display_user.pop("password_hash", None)
                    print("\n--- Detalles del Usuario ---")
                    for key, value in display_user.items():
                        print(f"{key.replace('_', ' ').title()}: {value}")
                    print("----------------------------")
                else:
                    print(f"Usuario con ID {user_id} no encontrado.")
            except ValueError:
                print("ID inválido. Por favor, ingrese un número.")

        elif choice == '4':
            username = input("Ingrese el nombre de usuario a buscar: ")
            user = user_manager.get_user_by_username(username)
            if user:
                display_user = user.copy()
                display_user.pop("password_hash", None)
                print("\n--- Detalles del Usuario ---")
                for key, value in display_user.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
                print("----------------------------")
            else:
                print(f"Usuario '{username}' no encontrado.")

        elif choice == '5':
            try:
                user_id = int(input("Ingrese el ID del usuario a actualizar: "))
                user = user_manager.get_user_by_id(user_id)
                if user:
                    print(f"Editando usuario: {user['username']}")
                    new_full_name = input(f"Nuevo nombre completo (actual: {user['full_name']}) [Dejar vacío para no cambiar]: ")
                    new_email = input(f"Nuevo correo electrónico (actual: {user['email']}) [Dejar vacío para no cambiar]: ")
                    new_password = input("Nueva contraseña [Dejar vacío para no cambiar]: ")
                    new_roles_str = input(f"Nuevos roles separados por coma (actual: {', '.join(user['roles'])}) [Dejar vacío para no cambiar]: ")
                    new_roles = [role.strip() for role in new_roles_str.split(',')] if new_roles_str else None

                    user_manager.update_user(
                        user_id,
                        new_full_name if new_full_name else None,
                        new_email if new_email else None,
                        new_password if new_password else None,
                        new_roles # Pasa None si está vacío, para que la función lo maneje
                    )
                else:
                    print(f"Usuario con ID {user_id} no encontrado para actualizar.")
            except ValueError:
                print("ID inválido. Por favor, ingrese un número.")

        elif choice == '6':
            try:
                user_id = int(input("Ingrese el ID del usuario a eliminar: "))
                user_manager.delete_user(user_id)
            except ValueError:
                print("ID inválido. Por favor, ingrese un número.")
        
        elif choice == '7':
            username = input("Ingrese nombre de usuario para autenticar: ")
            password = input("Ingrese contraseña para autenticar: ")
            authenticated_user = user_manager.authenticate_user(username, password)
            if authenticated_user:
                print(f"Bienvenido, {authenticated_user['full_name']} ({authenticated_user['username']}).")
            else:
                print("Autenticación fallida.")

        elif choice == '8':
            print("Saliendo del gestor de usuarios. ¡Hasta luego!")
            break
        
        else:
            print("Opción inválida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()