from datetime import datetime

class User:
    def __init__(self, db):
        self.db = db
    
    def create_user(self, nama, email, nomor_telepon, tanggal_lahir, jenis_kelamin, password, role='customer'):
        """
        Membuat user baru
        """
        try:
            cursor = self.db.cursor()
            
            # Insert user ke database dengan password plain text
            query = """
                INSERT INTO users (nama, email, nomor_telepon, tanggal_lahir, jenis_kelamin, password, role, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            now = datetime.now()
            cursor.execute(query, (nama, email, nomor_telepon, tanggal_lahir, jenis_kelamin, password, role, now, now))
            self.db.commit()
            cursor.close()
            
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user_by_email(self, email):
        """
        Mendapatkan user berdasarkan email
        """
        try:
            cursor = self.db.cursor()
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """
        Mendapatkan user berdasarkan ID
        """
        try:
            cursor = self.db.cursor()
            query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def verify_password(self, email, password):
        """
        Verifikasi password user (plain text)
        """
        user = self.get_user_by_email(email)
        if user and user['password'] == password:
            return user
        return None
    
    def email_exists(self, email):
        """
        Cek apakah email sudah terdaftar
        """
        user = self.get_user_by_email(email)
        return user is not None
    
    def update_user(self, user_id, data):
        """
        Update data user
        """
        try:
            cursor = self.db.cursor()
            
            # Build dynamic update query
            fields = []
            values = []
            
            for key, value in data.items():
                if key != 'id' and key != 'password':  # Jangan update id dan password melalui method ini
                    fields.append(f"{key} = %s")
                    values.append(value)
            
            if not fields:
                return False
            
            # Add updated_at
            fields.append("updated_at = %s")
            values.append(datetime.now())
            values.append(user_id)
            
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
            cursor.execute(query, values)
            self.db.commit()
            cursor.close()
            
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
