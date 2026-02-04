import requests
import json
import time

# ==============================
# CONFIGURATION SECTION
# ==============================

# Polaris endpoints
POLARIS_MANAGEMENT = "http://localhost:8181/api/management/v1"
AUTH = "http://localhost:8181/api/catalog/v1/oauth/tokens"
MINIO_EXTERNAL_URL = "http://localhost:9000"

# Admin bootstrap credentials (from POLARIS_BOOTSTRAP_CREDENTIALS)
ADMIN_CLIENT_ID = "root"
ADMIN_CLIENT_SECRET = "secret"

# Catalogs to create
CATALOG_NAMES = ["warehouse"]

# Principal to create (and give full access)
PRINCIPAL_NAME = "my_principal"

# ==============================
# SCRIPT LOGIC
# ==============================

def authenticate():
    """Authenticate to Polaris via OAuth2 client credentials flow"""
    payload = {
        "grant_type": "client_credentials",
        "client_id": ADMIN_CLIENT_ID,
        "client_secret": ADMIN_CLIENT_SECRET,
        "scope": "PRINCIPAL_ROLE:ALL"
    }
    for _ in range(20):
        try:
            r = requests.post(AUTH, data=payload)
            if r.status_code == 200:
                print("Authenticated as admin.")
                return r.json()["access_token"]
        except Exception:
            pass
        time.sleep(3)
    raise Exception("Polaris not ready or authentication failed.")

token = authenticate()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# --- 1. Ensure catalogs exist ---
def ensure_catalog(name):
    resp = requests.get(f"{POLARIS_MANAGEMENT}/catalogs/{name}", headers=headers)
    if resp.status_code == 200:
        print(f"Catalog '{name}' already exists.")
        return

    body = {
    "catalog": {
        "name": name,
        "type": "INTERNAL",
        "properties": {
            "default-base-location": f"s3://{name}/"
        },
        "storageConfigInfo": {
            "storageType": "S3",
            "allowedLocations": [f"s3://{name}/"],
            "region": "us-east-1",
            "endpointInternal": "http://minio:9000",
            "endpoint": MINIO_EXTERNAL_URL,
            "pathStyleAccess": True,
            "stsUnavailable": True,
            "roleArn": "arn:aws:iam::012345678901:role/polaris-role"
        }
    }
}

    r = requests.post(f"{POLARIS_MANAGEMENT}/catalogs", headers=headers, data=json.dumps(body))
    if r.status_code in [200, 201]:
        print(f"Catalog '{name}' created.")
    elif r.status_code == 409:
        print(f"Catalog '{name}' already exists (409).")
    else:
        print(f"Catalog '{name}' creation failed: {r.text}")

for cat in CATALOG_NAMES:
    ensure_catalog(cat)

# --- 2. Ensure principal exists and has credentials ---
def ensure_principal(name):
    resp = requests.get(f"{POLARIS_MANAGEMENT}/principals/{name}", headers=headers)
    if resp.status_code == 200:
        print(f"Principal '{name}' already exists.")
        return None

    body = {
        "principal": {"name": name, "properties": {"purpose": "demo"}},
        "credentialRotationRequired": False
    }
    r = requests.post(f"{POLARIS_MANAGEMENT}/principals", headers=headers, data=json.dumps(body))

    if r.status_code == 201:
        data = r.json()
        creds = data["credentials"]
        print(f"Created principal '{name}'.")
        print(f"CLIENT_ID = \"{creds['clientId']}\"")
        print(f"CLIENT_SECRET = \"{creds['clientSecret']}\"")
        return creds
    elif r.status_code == 409:
        print(f"Principal '{name}' already exists (409).")
        return None
    else:
        raise Exception(f"Failed to create principal: {r.text}")

creds = ensure_principal(PRINCIPAL_NAME)

# Rotate credentials if existing
if creds is None:
    r = requests.post(f"{POLARIS_MANAGEMENT}/principals/{PRINCIPAL_NAME}/reset", headers=headers)
    if r.status_code == 200:
        data = r.json()
        creds = data["credentials"]
        print(f"Rotated credentials for '{PRINCIPAL_NAME}'.")
        print(f"CLIENT_ID = \"{creds['clientId']}\"")
        print(f"CLIENT_SECRET = \"{creds['clientSecret']}\"")
    else:
        raise Exception(f"Failed to rotate credentials: {r.text}")

# --- 3. Create and assign roles ---
ROLE_NAME = f"{PRINCIPAL_NAME}_role"
role_body = {"principalRole": {"name": ROLE_NAME}}
requests.post(f"{POLARIS_MANAGEMENT}/principal-roles", headers=headers, data=json.dumps(role_body))
requests.put(f"{POLARIS_MANAGEMENT}/principals/{PRINCIPAL_NAME}/principal-roles", headers=headers, data=json.dumps(role_body))
print(f"Assigned principal role '{ROLE_NAME}' to '{PRINCIPAL_NAME}'.")

for cat in CATALOG_NAMES:
    cat_role = f"{cat}_role"
    cat_role_body = {"catalogRole": {"name": cat_role}}
    requests.post(f"{POLARIS_MANAGEMENT}/catalogs/{cat}/catalog-roles", headers=headers, data=json.dumps(cat_role_body))
    requests.put(
        f"{POLARIS_MANAGEMENT}/principal-roles/{ROLE_NAME}/catalog-roles/{cat}",
        headers=headers,
        data=json.dumps(cat_role_body)
    )
    grant_body = {
        "grant": {"type": "catalog", "privilege": "CATALOG_MANAGE_CONTENT"}
    }
    requests.put(
        f"{POLARIS_MANAGEMENT}/catalogs/{cat}/catalog-roles/{cat_role}/grants",
        headers=headers,
        data=json.dumps(grant_body)
    )
    print(f"Granted full access on '{cat}'.")

print("\nPolaris setup complete.\n")
