from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, nome, cognome, is_partecipante):
        self.id = id
        self.email = email
        self.password = password
        self.nome = nome
        self.cognome = cognome
        self.is_partecipante = is_partecipante