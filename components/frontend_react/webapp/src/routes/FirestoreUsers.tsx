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

import Loading from "@/navigation/Loading"
import { db } from "@/utils/firebase"
import { snapToDocument } from "@/utils/firestore"
import { DocumentData, collection, onSnapshot } from "firebase/firestore"
import { useEffect, useState } from "react"

const FirestoreUsersRoute = () => {
  const [users, setUsers] = useState<DocumentData[] | null>(null)

  useEffect(() => {
    // Add/Edit users here to see it react in real-time
    // https://console.firebase.google.com/project/genie-ui-dev/firestore/data/~2Fusers~2F5uvix17Bw41BC0qHv3Kc
    onSnapshot(collection(db, "users"), (snapshot) => {
      // Can use a zod.parse for type guarantees
      setUsers(snapshot.docs.map(snapToDocument))
    })
  }, [])

  if (!users) {
    return <Loading />
  }

  return (
    <div>
      <p className="pb-10">
        Add/Edit users{" "}
        <a
          className="link link-primary"
          target="_blank"
          rel="noopener"
          href="https://console.firebase.google.com/project/genie-ui-dev/firestore/data/~2Fusers~2F5uvix17Bw41BC0qHv3Kc"
        >
          here
        </a>{" "}
        to see it react in real-time
      </p>
      {users.map((user) => (
        <div key={user.id}>
          @{user.id} - {user.name} - {user.email}
        </div>
      ))}
    </div>
  )
}

export default FirestoreUsersRoute
