import os
import pytest
from kis import config


@pytest.mark.parametrize(
    "id, secret_key, app_key, account, virtual_id, virtual_secret_key, virtual_app_key, virtual_account",
    [
        (
            "test-id",
            "test-secret",
            "test-app",
            "test-account",
            "test-virtual-id",
            "test-virtual-secret",
            "test-virtual-app",
            "test-virtual-account",
        ),
        (
            "test-id-2",
            "test-secret-2",
            "test-app-2",
            "test-account-2",
            "test-virtual-id-2",
            "test-virtual-secret-2",
            "test-virtual-app-2",
            "test-virtual-account-2",
        ),
    ],
)
def test_load_config(
    id: str,
    secret_key: str,
    app_key: str,
    account: str,
    virtual_id: str,
    virtual_secret_key: str,
    virtual_app_key: str,
    virtual_account: str,
):
    os.environ["KIS_ID"] = id
    os.environ["KIS_SECRET_KEY"] = secret_key
    os.environ["KIS_APP_KEY"] = app_key
    os.environ["KIS_ACCOUNT"] = account
    os.environ["KIS_VIRTUAL_ID"] = virtual_id
    os.environ["KIS_VIRTUAL_SECRET_KEY"] = virtual_secret_key
    os.environ["KIS_VIRTUAL_APP_KEY"] = virtual_app_key
    os.environ["KIS_VIRTUAL_ACCOUNT"] = virtual_account

    cfg = config.load_config()

    assert cfg.id == id
    assert cfg.secret_key == secret_key
    assert cfg.app_key == app_key
    assert cfg.account == account
    assert cfg.virtual_id == virtual_id
    assert cfg.virtual_secret_key == virtual_secret_key
    assert cfg.virtual_app_key == virtual_app_key
    assert cfg.virtual_account == virtual_account
