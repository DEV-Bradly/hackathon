"""Firebase Admin SDK initialization.

This module initializes the Firebase Admin app for server-side usage, using a
service account. The JSON credentials can be provided via:
- A file path in environment variable FIREBASE_CREDENTIALS_FILE
- A JSON string in environment variable FIREBASE_CREDENTIALS_JSON

Firestore and Auth are exposed via helper functions.
"""
from __future__ import annotations
import json
import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore, auth


_admin_app: Optional[firebase_admin.App] = None


def initialize_firebase() -> firebase_admin.App:
    global _admin_app
    if _admin_app is not None:
        return _admin_app

    creds_file = os.environ.get("FIREBASE_CREDENTIALS_FILE")
    creds_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")

    if creds_file:
        cred = credentials.Certificate(creds_file)
    elif creds_json:
        cred_dict = json.loads(creds_json)
        cred = credentials.Certificate(cred_dict)
    else:
        raise RuntimeError(
            "Firebase credentials not provided. Set FIREBASE_CREDENTIALS_FILE or FIREBASE_CREDENTIALS_JSON."
        )

    _admin_app = firebase_admin.initialize_app(cred)
    return _admin_app


def get_firestore_client() -> firestore.Client:
    initialize_firebase()
    return firestore.client()


def verify_id_token(id_token: str) -> dict:
    initialize_firebase()
    return auth.verify_id_token(id_token)
