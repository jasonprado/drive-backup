#!/usr/bin/env python3
"""Backs up specified files from Google Drive.
"""

import datetime
import os
import csv
import yaml
import tempfile
import gspread
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pprint import pprint
import minio


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/spreadsheets']
DATE_STRING = datetime.datetime.now().strftime('%Y-%m-%d')

def run(
  files_path,
  minio_host,
  minio_access_key,
  minio_secret_key,
  minio_bucket,
  google_credential_path,
):
  google_credentials = ServiceAccountCredentials.from_json_keyfile_name(
    google_credential_path, scopes=SCOPES)

  gauth = GoogleAuth()
  gauth.credentials = google_credentials
  gauth.ServiceAuth()
  drive = GoogleDrive(gauth)
  gspread_service = gspread.service_account(filename=google_credential_path)

  with open(files_path) as files_file:
    files = yaml.load(files_file, Loader=yaml.FullLoader)

  minio_client = minio.Minio(minio_host, minio_access_key, minio_secret_key, secure=False)

  download_dir = tempfile.mkdtemp()
  for file in files['files']:
    downloaded_path = get_file(drive, gspread_service, download_dir, file)
    minio_client.fput_object(minio_bucket, os.path.basename(downloaded_path), downloaded_path)


def get_file(drive, gspread_service, download_dir, file):
    drive_file_id = file['id']
    file_name_template = file['name']
    file_name = file_name_template.replace('{DATE}', DATE_STRING)
    file_path = os.path.join(download_dir, file_name)

    drive_file = drive.CreateFile({ 'id': drive_file_id })
    drive_file.FetchMetadata()

    if drive_file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
      sheet = gspread_service.open_by_key(drive_file_id)
      worksheet = sheet.worksheets()[0]
      with open(file_path, 'w') as f:
        writer = csv.writer(f)
        rows = worksheet.get_all_values()
        writer.writerows(rows)

    return file_path


def main():
  from dotenv import load_dotenv
  load_dotenv()
  run(
    files_path=os.getenv('FILES_PATH'),
    minio_host=os.getenv('MINIO_HOST'),
    minio_access_key=os.getenv('MINIO_ACCESS_KEY'),
    minio_secret_key=os.getenv('MINIO_SECRET_KEY'),
    minio_bucket=os.getenv('MINIO_BUCKET'),
    google_credential_path=os.getenv('GOOGLE_CREDENTIAL_PATH'),
  )

if __name__ == '__main__':
  main()
