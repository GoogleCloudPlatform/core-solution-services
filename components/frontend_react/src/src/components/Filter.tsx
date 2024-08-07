/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { CASE_STATUSES, CASE_TYPES } from "@/utils/types"

export default function Filter() {
  return (
    <div className="mb-6 flex gap-8 rounded-md border p-4">
      <div className="w-4/5">
        <div className="gri-cols-2 grid gap-4 lg:grid-cols-4">
          <label className="form-control w-full max-w-xs">
            <div className="label">
              <span className="label-text font-semibold">Assigned To</span>
            </div>
            <select className="select select-sm select-bordered w-full max-w-xs">
              <option disabled selected>
                Any
              </option>
              <option>Heather Braxton</option>
              <option>Jeremy Clark</option>
              <option>Rachelle Harper</option>
            </select>
          </label>
          <label className="form-control w-full max-w-xs">
            <div className="label">
              <span className="label-text font-semibold">Case Status</span>
            </div>
            <select className="select select-sm select-bordered w-full max-w-xs">
              <option disabled selected>
                Any
              </option>
              $
              {CASE_STATUSES.map((status) => (
                <option key={status}>{status}</option>
              ))}
            </select>
          </label>
          <label className="form-control w-full max-w-xs">
            <div className="label">
              <span className="label-text font-semibold">Case Type</span>
            </div>
            <select className="select select-sm select-bordered w-full max-w-xs">
              <option disabled selected>
                Any
              </option>
              {CASE_TYPES.map((type) => (
                <option key={type}>{type}</option>
              ))}
            </select>
          </label>
          <label className="form-control w-full max-w-xs">
            <div className="label">
              <span className="label-text font-semibold">Search Cases</span>
            </div>
            <input
              type="text"
              placeholder="Type here"
              className="input input-sm input-bordered w-full max-w-xs"
            />
          </label>
        </div>
      </div>
      <div className="w-1/5">
        <div className="flex flex-col">
          <button className="btn btn-link btn-sm hover-underline no-underline">
            Reset
          </button>
          <button className="btn btn-primary btn-sm">Apply</button>
        </div>
      </div>
    </div>
  )
}
