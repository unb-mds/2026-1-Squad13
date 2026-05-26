from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from domain.exceptions import TokenRevogadoError
from presentation.auth_dependencies import get_current_user


def test_get_current_user_sucesso():
    auth_service = MagicMock()
    user = MagicMock()
    auth_service.user_repository.buscar_por_email.return_value = user

    with patch("presentation.auth_dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}

        result = get_current_user(token="valid_token", auth_service=auth_service)

        assert result == user
        auth_service.verificar_token_blacklist.assert_called_once_with("valid_token")


def test_get_current_user_token_revogado():
    auth_service = MagicMock()
    auth_service.verificar_token_blacklist.side_effect = TokenRevogadoError()

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="revoked_token", auth_service=auth_service)
    assert exc.value.status_code == 401


def test_get_current_user_email_ausente():
    auth_service = MagicMock()
    with patch("presentation.auth_dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {}  # No sub

        with pytest.raises(HTTPException) as exc:
            get_current_user(token="token", auth_service=auth_service)
        assert exc.value.status_code == 401


def test_get_current_user_usuario_nao_encontrado():
    auth_service = MagicMock()
    auth_service.user_repository.buscar_por_email.return_value = None

    with patch("presentation.auth_dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": "ghost@example.com"}

        with pytest.raises(HTTPException) as exc:
            get_current_user(token="token", auth_service=auth_service)
        assert exc.value.status_code == 401
