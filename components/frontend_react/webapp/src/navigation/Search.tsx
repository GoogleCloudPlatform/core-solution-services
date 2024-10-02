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

interface SearchProps {}

const Search: React.FunctionComponent<SearchProps> = ({}) => {
  return (
    <div className="border-base-300 relative flex h-full flex-grow items-center gap-4 rounded-lg border px-2">
      <div className="i-heroicons-magnifying-glass pointer-events-none absolute h-5 w-5 opacity-70" />
      <input
        className="bg-base-100 w-full py-1 pl-8 outline-none"
        placeholder="Search"
      />
    </div>
  )
}

export default Search
