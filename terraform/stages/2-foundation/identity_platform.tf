/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

#added so we can append random suffix to the IDP key
resource "random_id" "key_suffix" {
  byte_length = 8
}

#adding random suffix to avid the problem caused when you do a destroy.  The Key 
#is deleted, but remains for 30 days so its name can't be reused.  
resource "google_apikeys_key" "idp_api_key" {
  depends_on   = [time_sleep.wait_60_seconds]
  name         = "idp-api-key-${random_id.key_suffix.hex}"
  display_name = "API Key for Identity Platform"

  restrictions {
    api_targets {
      service = "identitytoolkit.googleapis.com"
    }
  }
}

resource "google_secret_manager_secret" "firebase-api-key" {
  depends_on = [time_sleep.wait_60_seconds]
  secret_id = var.firebase_api_secret_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secret_api_key" {
  secret = google_secret_manager_secret.firebase-api-key.id
  secret_data = google_apikeys_key.idp_api_key.key_string
}

