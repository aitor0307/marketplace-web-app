"""Single place where every Flask extension is instantiated.

Extensions are created unbound here and wired to a concrete app inside
``create_app`` via ``init_app``. This is what lets the app factory build
more than one app instance (e.g. one per test) without extensions leaking
state between them.
"""
import redis
from flask_bootstrap import Bootstrap5
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "views_auth.login"
mail = Mail()
bootstrap = Bootstrap5()
moment = Moment()
jwt = JWTManager()


class RedisClient:
    """Thin lazy wrapper around a redis-py client.

    Nothing in the app talks to Redis yet, but the connection is fully
    configured so caching, rate limiting, or a vector index (RediSearch /
    redis-vector) can be added later without touching config or the
    factory again.
    """

    def __init__(self):
        self._client = None

    def init_app(self, app):
        self._client = redis.from_url(
            app.config["REDIS_URL"], decode_responses=True
        )
        app.extensions["redis"] = self._client

    @property
    def client(self):
        if self._client is None:
            raise RuntimeError("RedisClient.init_app(app) has not been called yet")
        return self._client

    def ping(self):
        try:
            return self.client.ping()
        except redis.exceptions.RedisError:
            return False


redis_client = RedisClient()

"""
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from pytz import timezone
from datetime import datetime, timedelta


class StorageAccount:
    def __init__(self, container_name=Config.USER_DOCUMENTS):
        self.sas_key = Config.AZURE_BLOB_STORAGE_ACCOUNT_KEY
        self.container_name = container_name
        self.expiry = datetime.now() + timedelta(days=365 * 5)
        self.blob_service_client = BlobServiceClient(account_url=Config.AZURE_BLOB_STORAGE_URL, credential=get_credential())
        self.container_client = self.blob_service_client.get_container_client(container_name)
        try:
            self.container_client.create_container()
        except ResourceExistsError:
            pass
    
    def upload_doc(self, file_path, blob_name, file_content=None):
        if not file_content:
            with open(file_path, "rb") as f:
                file_content = f.read()
        blob_client = self.container_client.get_blob_client(blob_name)
        # Upload the content to the blob
        blob_client.upload_blob(file_content, overwrite=True)
        return 200
    
    def list_blobs(self):
        blob_list = self.container_client.list_blobs()
        return [blob.name for blob in blob_list]
            
    def generate_url(self, blob_name, expiry=None):
        if expiry is None:
            expiry = self.expiry
    
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=Config.AZURE_BLOB_STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=expiry
        )
        
        blob_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
        return blob_url
    
    def get_blob(self, blob_name):
        stream = io.BytesIO()
        return self.container_client.download_blob(blob_name).readinto(stream)
    
    def download_blob_to_file(self, blob_name, filepath):
        stream = io.BytesIO()
        with open(file=os.path.join(filepath, blob_name), mode="wb") as sample_blob:
            sample_blob.write(self.container_client.download_blob(blob_name).readinto(stream).readall())
    
    def upload_document_and_get_url(self, file_path, folder_name=None, expiry=None):
        blob_name = folder_name + '/' + os.path.basename(file_path) if folder_name else os.path.basename(file_path)
        self.upload_doc(file_path, blob_name)
        blob_url_with_sas = self.generate_url(blob_name, expiry=expiry)
        return blob_url_with_sas
    
    def delete_doc(self, blob_url_with_sas):
        blob_name = blob_url_with_sas.split('?')[0].split('/')[-1]
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_exists = blob_client.exists()
        if not blob_exists:
            logger.error(f"Blob {blob_name} does not exist in the container.")
            raise Exception(f"Blob {blob_name} does not exist in the container.")
        blob_client.delete_blob()

        return None
    
    @staticmethod
    def partially_encode_url(url):
        parsed_url = urllib.parse.urlparse(url)
        encoded_path = urllib.parse.quote(parsed_url.path)
        urlunparse = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, encoded_path, parsed_url.params, parsed_url.query, parsed_url.fragment))
        return urlunparse
    
    def whatsapp_document_upload(self, company_id, media_id):
        whatsapp_token = db.session.query(CompanySettings).filter_by(company_id=company_id, name="whatsapp_token").first().value
        media_url = f'https://graph.facebook.com/v18.0/{media_id}'
        media_response = requests.get(
            media_url,
            headers={'Authorization': f'Bearer {whatsapp_token}'}
        )
        
        if media_response.status_code == 200:
            logger.debug("media_response: %s", media_response.json())
            media_url = media_response.json().get('url')
            mime_type = media_response.json().get('mime_type')
                    # Hacer una solicitud GET a la URL del archivo de audio
            response = requests.get(
                        media_url,
                        headers={'Authorization': f'Bearer {whatsapp_token}'})
                    # Guardar el contenido de la respuesta en un archivo
            blob_name = f"whatsapp_{media_id}.{mime_type.split('/')[1]}"
            
            media_content = response.content
            self.upload_doc("", blob_name, media_content)
            blob_url_with_sas = self.generate_url(blob_name, expiry=(datetime.now(timezone('Europe/Madrid')) + timedelta(days=90)))
            return blob_url_with_sas
        else:
            # Manejar errores
            logger.error("Error al descargar el archivo multimedia de WhatsApp:", response.text)
            return None
"""