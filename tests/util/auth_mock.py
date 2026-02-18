from service.auth import login_manager


def mock_logged_in_user(app):
    def _get_logged_in_user():
        return "mock-user"

    app.dependency_overrides[login_manager] = _get_logged_in_user
