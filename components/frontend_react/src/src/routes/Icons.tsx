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

const IconsRoute = () => {
  return (
    <>
      <h1 className="pb-6 pt-2 text-2xl">Dynamic Icons</h1>
      <p>
        Easy access to{" "}
        <a
          className="link link-primary"
          href="https://icones.js.org/"
          target="_blank"
          rel="noopener"
        >
          150,000+ icons
        </a>{" "}
        with a few lines of code.
      </p>
      <p>
        Read more{" "}
        <a
          className="link link-primary"
          href="https://unocss.dev/presets/icons"
          target="_blank"
          rel="noopener"
        >
          here
        </a>
      </p>
      <div className="flex flex-col gap-y-8 py-10">
        <div className="flex items-center gap-x-8">
          <div className="w-24">Heroicons</div>

          <div className="mockup-code flex-grow">
            <pre>
              <code>{`<div className="i-heroicons-cake text-error h-10 w-10" />`}</code>
            </pre>
          </div>
          <div className="i-heroicons-cake text-error h-10 w-10 w-32" />
        </div>
        <div className="flex items-center gap-x-8">
          <div className="w-24">Material UI</div>

          <div className="mockup-code flex-grow">
            <pre>
              <code>{`<div className="i-mdi-alarm text-primary text-3xl" />`}</code>
            </pre>
          </div>
          <div className="i-mdi-alarm text-primary w-32 text-3xl" />
        </div>
        <div className="flex items-center gap-x-8">
          <div className="w-24">Logos</div>

          <div className="mockup-code flex-grow">
            <pre>
              <code>{`<div className="i-logos-apigee text-5xl" />`}</code>
            </pre>
          </div>
          <div className="i-logos-apigee w-32 text-5xl" />
        </div>
      </div>
    </>
  )
}

export default IconsRoute
