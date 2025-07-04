import jwt
import time    
epoch_time = int(time.time())
with open("../mushare.p8", mode = "rb") as f:
    private_key = f.read()

encoded = jwt.encode({ "iss": "35364D4N7T", "iat": 1751520047, "exp": 1762187848 } , private_key, algorithm="ES256", headers={"kid": "957579S4C8" })

# jwt.encode( {"some": "payload"}, "secret", algorithm="HS256", headers={"kid": ""}, )