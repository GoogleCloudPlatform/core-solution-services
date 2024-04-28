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

import { db } from "@/utils/firebase"
import {
  addDoc as addDocument,
  collection,
  deleteDoc as deleteDocument,
  doc,
  DocumentData,
  DocumentSnapshot,
  getDoc,
  getDocs,
  query,
  QueryConstraint,
  QueryDocumentSnapshot,
  serverTimestamp,
  updateDoc as updateDocument,
  where,
  WhereFilterOp,
  writeBatch,
} from "firebase/firestore"

export const snapToDocument = (
  snap: QueryDocumentSnapshot | DocumentSnapshot,
): DocumentData => ({
  ...snap.data(),
  id: snap.id,
})

export const getAllDocs = (path: string) =>
  getDocs(collection(db, path)).then((snap) => snap.docs.map(snapToDocument))

export const getDocById = (path: string, id: string) =>
  getDoc(doc(db, path, id)).then((snap) =>
    snap.exists() ? snapToDocument(snap) : null,
  )

export const getDocSnapsByQuery = (
  path: string,
  conditions: QueryConstraint[],
) => getDocs(query(collection(db, path), ...conditions))

export const getDocsByQuery = (path: string, conditions: QueryConstraint[]) =>
  getDocSnapsByQuery(path, conditions).then((snap) =>
    snap.docs.map(snapToDocument),
  )

export const getDocsByField = (
  path: string,
  field: string,
  value: string,
  operator: WhereFilterOp = "==",
) => getDocsByQuery(path, [where(field, operator, value)])

export const addDoc = (path: string, data: DocumentData) =>
  addDocument(collection(db, path), {
    ...data,
    createdAt: serverTimestamp(),
  })

export const updateDoc = (path: string, id: string, body: DocumentData) =>
  updateDocument(doc(db, path, id), {
    ...body,
    updatedAt: serverTimestamp(),
    createdAt: body.createdAt ?? serverTimestamp(),
  })

export const deleteDoc = (path: string, id: string) =>
  deleteDocument(doc(db, path, id))

export const deleteDocsByQuery = async (
  path: string,
  conditions: QueryConstraint[],
) => {
  const snaps = await getDocSnapsByQuery(path, conditions)
  const batch = writeBatch(db)
  snaps.forEach((snap) => batch.delete(snap.ref))
  return batch.commit()
}

export const deleteDocsByField = (
  path: string,
  field: string,
  value: string,
  operator: WhereFilterOp = "==",
) => deleteDocsByQuery(path, [where(field, operator, value)])
