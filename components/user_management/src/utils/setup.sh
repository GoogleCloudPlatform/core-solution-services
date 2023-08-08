# Add a default "admin" user to the Firestore.

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "document": {
      "fields": {
        "name": "admin",
        "email": "$EMAIL"
      }
    }
  }' \
  "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/users/admin"
