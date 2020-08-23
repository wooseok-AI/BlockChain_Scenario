from ecdsa import SigningKey, NIST384p

sk = SigningKey.generate(curve = NIST384p)
vk = sk.get_verifying_key()
signature = sk.sign("0123".encode)
print(vk.verify(signature, "0123".encode))
# 
# try:
#     print(vk.verify(signature, 'message'.encode))
# except Exception:
#     print('확인실패')