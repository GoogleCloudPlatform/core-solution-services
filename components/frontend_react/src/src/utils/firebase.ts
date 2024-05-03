// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the License);
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { OAuthScopes } from "@/utils/AppConfig"
import { envOrFail } from "@/utils/env"
import {
  logEvent as fbLogEvent,
  getAnalytics as getFirebaseAnalytics,
} from "firebase/analytics"
import { FirebaseApp, getApp, initializeApp } from "firebase/app"
import { GoogleAuthProvider, getAuth } from "firebase/auth"
import { getFirestore } from "firebase/firestore"
import { connectFunctionsEmulator, getFunctions } from "firebase/functions"
import { connectStorageEmulator, getStorage } from "firebase/storage"

const apiKey = envOrFail(
  "VITE_FIREBASE_PUBLIC_API_KEY",
  import.meta.env.VITE_FIREBASE_PUBLIC_API_KEY,
)

const authDomain = envOrFail(
  "VITE_FIREBASE_AUTH_DOMAIN",
  import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
)

const projectId = envOrFail(
  "VITE_FIREBASE_PROJECT_ID",
  import.meta.env.VITE_FIREBASE_PROJECT_ID,
)

const storageBucket = envOrFail(
  "VITE_FIREBASE_STORAGE_BUCKET",
  import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
)

const messagingSenderId = envOrFail(
  "VITE_FIREBASE_MESSAGING_SENDER_ID",
  import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
)

const appId = envOrFail(
  "VITE_FIREBASE_APP_ID",
  import.meta.env.VITE_FIREBASE_APP_ID,
)

// const measurementId = envOrFail(
//   "VITE_FIREBASE_MEASUREMENT_ID",
//   import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
// )

const firebaseConfig = {
  apiKey,
  authDomain,
  projectId,
  storageBucket,
  messagingSenderId,
  appId,
}

let app: FirebaseApp
try {
  app = getApp()
} catch (_) {
  app = initializeApp(firebaseConfig)
}

const getAnalytics = () => {
  return getFirebaseAnalytics(app)
}

const logEvent = (eventName: string, eventParams?: { [key: string]: any }) => {
  import.meta.env.DEV
    ? console.debug("Dev logging event:", eventName, eventParams)
    : fbLogEvent(getAnalytics(), eventName, eventParams)
}

const auth = getAuth(app)
auth.useDeviceLanguage()

const db = getFirestore(app)
const functions = getFunctions(app)
const storage = getStorage(app)

const googleProvider = new GoogleAuthProvider()
OAuthScopes.forEach((scope) => googleProvider.addScope(scope))

if (import.meta.env.DEV) {
  try {
    console.debug("Connecting Firebase Emulators")
    connectStorageEmulator(storage, "localhost", 9199)
    connectFunctionsEmulator(functions, "localhost", 5001)
  } catch (_) {
    console.warn("Failed to connect to Firebase emulators")
  }
}

export {
  app,
  auth,
  db,
  functions,
  getAnalytics,
  googleProvider,
  logEvent,
  storage,
}
