class UserRouter:
    """
    A router to control all database operations on models in
    the auth and related apps (User) to go to 'user_cid'.
    """
    route_app_labels = {'auth', 'User'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and user models go to user_cid.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'user_cid'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and user models go to user_cid.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'user_cid'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow any relation if a model in route_app_labels is involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label in self.route_app_labels:
            return db == 'user_cid'
        return None