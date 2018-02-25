from unittest.mock import patch
import pytest
import gdax


@pytest.fixture
def client():
    return gdax.PublicClient()


@pytest.mark.parametrize("code, exception",[
                         (400, gdax.exceptions.InvalidGdaxRequest),
                         (401, gdax.exceptions.UnauthorizedGdaxRequest),
                         (403, gdax.exceptions.ForbiddenGdaxRequest),
                         (404, gdax.exceptions.NotFoundGdaxRequest),
                         (422, gdax.exceptions.UnknownGdaxClientRequest),
                         (500, gdax.exceptions.InternalErrorGdaxRequest)])
@patch('requests.get')
def test_gdax_exceptions(mock_request, client, code, exception):
    mock_request.return_value.status_code = code
    with pytest.raises(exception):
        client.get_products()
