from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64

# 🏠 Home Page
def home(request):
    return render(request, 'encryptor/home.html')


# 🔐 AES Encryption + RSA key generation
def encrypt_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_data = uploaded_file.read()

        # Step 1 – AES encryption
        aes_key = get_random_bytes(16)
        cipher_aes = AES.new(aes_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(file_data)

        # Step 2 – Generate RSA keypair (for demo, generated each time)
        rsa_key = RSA.generate(2048)
        private_key = rsa_key.export_key()
        public_key = rsa_key.publickey().export_key()

        # Step 3 – Encrypt AES key using RSA public key
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(public_key))
        enc_aes_key = cipher_rsa.encrypt(aes_key)

        # Step 4 – Save encrypted file
        encrypted_filename = f"encrypted_{uploaded_file.name}"
        default_storage.save(encrypted_filename, ContentFile(ciphertext))

        # Step 5 – Encode everything for HTML display
        context = {
            'encrypted_file': encrypted_filename,
            'public_key': base64.b64encode(public_key).decode('utf-8'),
            'private_key': base64.b64encode(private_key).decode('utf-8'),
            'enc_aes_key': base64.b64encode(enc_aes_key).decode('utf-8'),
            'aes_nonce': base64.b64encode(cipher_aes.nonce).decode('utf-8'),
        }

        return render(request, 'encryptor/encrypt_result.html', context)

    return render(request, 'encryptor/encrypt.html')


# 🔓 Decrypt File using RSA + AES
def decrypt_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            # Collect inputs
            enc_file = request.FILES['file']
            enc_aes_key_b64 = request.POST.get('enc_aes_key')
            private_key_b64 = request.POST.get('private_key')
            nonce_b64 = request.POST.get('aes_nonce')

            # Basic validation
            if not (enc_aes_key_b64 and private_key_b64 and nonce_b64):
                raise ValueError("All fields are required for decryption.")

            # Decode Base64 inputs
            private_key = RSA.import_key(base64.b64decode(private_key_b64))
            enc_aes_key = base64.b64decode(enc_aes_key_b64)
            nonce = base64.b64decode(nonce_b64)
            ciphertext = enc_file.read()

            # Step 1 – RSA decryption of AES key
            cipher_rsa = PKCS1_OAEP.new(private_key)
            aes_key = cipher_rsa.decrypt(enc_aes_key)

            # Step 2 – AES decryption of file
            cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
            decrypted_data = cipher_aes.decrypt(ciphertext)

            # Step 3 – Save decrypted file
            decrypted_filename = f"decrypted_{enc_file.name}"
            default_storage.save(decrypted_filename, ContentFile(decrypted_data))

            return render(request, 'encryptor/decrypt_result.html', {
                'decrypted_file': decrypted_filename,
                'error': None
            })

        except Exception as e:
            return render(request, 'encryptor/decrypt_result.html', {
                'error': str(e),
                'decrypted_file': None
            })

    return render(request, 'encryptor/decrypt.html')
