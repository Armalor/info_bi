import json
from jwkest import BadSignature
from jwkest.jwk import KEYS
from jwkest.jws import JWS
import logging
from urllib.request import Request, urlopen


# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.__str__()
sys.path.append(__root__)
from esia.tools import base64_urldecode
from esia.tools import get_ssl_context
# ~Локальный импорт


logger = logging.getLogger("uvicorn.default")


class JwtValidatorException(Exception):
    pass


class JwtValidator:
    def __init__(self, config):
        logger.info('Getting ssl context for jwks_uri')
        self.ctx = get_ssl_context(config)

        self.jwks_uri = config['jwks_uri']
        self.jwks = self.load_keys()

    def validate(self, jwt, iss, aud):
        parts = jwt.split('.')
        if len(parts) != 3:
            raise BadSignature('Invalid JWT. Only JWS supported.')
        header = json.loads(base64_urldecode(parts[0]))
        payload = json.loads(base64_urldecode(parts[1]))

        if iss != payload['iss']:
            raise JwtValidatorException("Invalid issuer %s, expected %s" % (payload['iss'], iss))

        if payload["aud"]:
            if (isinstance(payload["aud"], str) and payload["aud"] != aud) or aud not in payload['aud']:
                raise JwtValidatorException("Invalid audience %s, expected %s" % (payload['aud'], aud))

        jws = JWS(alg=header['alg'])
        # Raises exception when signature is invalid
        try:
            jws.verify_compact(jwt, self.jwks)
        except Exception as e:
            print("Exception validating signature")
            raise JwtValidatorException(e)
        print("Successfully validated signature.")

    def get_jwks_data(self):
        request = Request(self.jwks_uri)
        request.add_header('Accept', 'application/json')
        request.add_header('User-Agent', 'CurityExample/1.0')

        try:
            jwks_response = urlopen(request, context=self.ctx)
        except Exception as e:
            print("Error fetching JWKS", e)
            raise e
        return jwks_response.read()

    def load_keys(self):
        # load the jwk set.
        jwks = KEYS()
        jwks.load_jwks(self.get_jwks_data())
        return jwks
