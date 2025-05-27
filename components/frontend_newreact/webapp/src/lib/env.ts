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

export const envOrFail = (
  name: string,
  value: string | undefined,
  fallback?: string,
): string => {
  // Must explicitly pass in process.env.VAR_NAME otherwise NextJS won't load it
  // Can't do dynamic variables like: process.env[name]
  // https://nextjs.org/docs/basic-features/environment-variables
  if (typeof value === "undefined" || value === "") {
    if (fallback) {
      console.warn(`${name} was not set. Defaulting to ${fallback}`);
      return fallback;
    }
    throw new Error(`${name} is not set`);
  }
  return value;
};

export const getEnvVars = () => ({
  VITE_PUBLIC_API_ENDPOINT: 'https://your-domain-name/llm-service/api/v1',
  VITE_PUBLIC_API_JOBS_ENDPOINT: 'https://your-domain-name/jobs-service/api/v1',
});
