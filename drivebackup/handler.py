from .drivebackup import run
import dotenv

def handle(_):
  config = dotenv.dotenv_values("/var/openfaas/secrets/drivebackup-config.env")
  run(
    files_path=config['FILES_PATH'],
    minio_host=config['MINIO_HOST'],
    minio_access_key=config['MINIO_ACCESS_KEY'],
    minio_secret_key=config['MINIO_SECRET_KEY'],
    minio_bucket=config['MINIO_BUCKET'],
    google_credential_path=config['GOOGLE_CREDENTIAL_PATH'],
  )
  return '{"status":"ok"}'
