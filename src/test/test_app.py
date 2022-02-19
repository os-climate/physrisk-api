from physrisk_api.app import create_app


def test_home():
    """Ensure index returns Hello World message."""

    app = create_app()

    with app.test_client() as test_client:
        resp = test_client.get("/")

        assert resp.status_code == 200
        assert resp.data == b"Hello World!"
