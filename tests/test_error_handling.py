from unittest.mock import patch
import pytest
import cbpro


@pytest.fixture
def client():
    return cbpro.PublicClient()


@pytest.mark.parametrize("code, exception",[
                         (400, cbpro.exceptions.InvalidCbproRequest),
                         (401, cbpro.exceptions.UnauthorizedCbproRequest),
                         (403, cbpro.exceptions.ForbiddenCbproRequest),
                         (404, cbpro.exceptions.NotFoundCbproRequest),
                         (422, cbpro.exceptions.UnknownCbproClientRequest),
                         (429, cbpro.exceptions.CbproRateLimitRequest),
                         (500, cbpro.exceptions.InternalErrorCbproRequest)])
@patch('requests.Session.request')
def test_cbpro_exceptions(mock_request, client, code, exception):
    mock_request.return_value.status_code = code
    with pytest.raises(exception):
        response = client.get_products()
