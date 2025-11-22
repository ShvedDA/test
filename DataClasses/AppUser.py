class AppUser:
    def __init__(self, master):
        self.master = master
        self.login_name: str = None
        self.authorise = False

    def set_data(self, username, failed=False):
        """Устанавлием если был успешный вход по-умолчанию"""
        self.login_name = username
        self.authorise = not failed

    def logout_user(self):
        self.login_name = None
        self.authorise = False
