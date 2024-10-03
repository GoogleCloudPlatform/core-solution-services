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

// You may need to remove "type": "module" in package.json

import { Translate } from "@google-cloud/translate/build/src/v2"
import { Promise as bluebird } from "bluebird"
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises"
import { difference } from "ramda"
import { supportedLangs } from "../src/utils/lang"

const translateClient = new Translate()
const targetLanguages = supportedLangs
  .map((lang) => lang.code)
  .filter((lang) => lang !== "en")

const SOURCE_BASE = "public/locales"
const ENGLISH_BASE = `${SOURCE_BASE}/en`
const CONCURRENCY = 3

const fileExists = async (path: string) =>
  !!(await stat(path).catch((_) => false))

const ensureLanguageFileExists = async (dir: string, file: string) => {
  if (!(await fileExists(dir))) {
    try {
      await mkdir(dir)
    } catch (_) {}
  }

  if (!(await fileExists(file))) {
    await writeFile(file, JSON.stringify({}))
  }
}

async function main() {
  const sourceFiles = await readdir(ENGLISH_BASE)
  sourceFiles.forEach(async (sourceFile) => {
    const sourcePhrases = JSON.parse(
      await readFile(`${ENGLISH_BASE}/${sourceFile}`, "utf8"),
    ) as Record<string, string>

    await bluebird.map(
      targetLanguages,
      async (targetLanguage: string) => {
        console.log("LANG: ", targetLanguage)
        const targetDir = `${SOURCE_BASE}/${targetLanguage}`
        const targetFile = `${targetDir}/${sourceFile}`

        await ensureLanguageFileExists(targetDir, targetFile)
        const targetPhrases = JSON.parse(
          await readFile(targetFile, "utf8"),
        ) as Record<string, string>

        // Delete phrases from "en" version to have them deleted from all others
        const deletePhrases = difference(
          Object.keys(targetPhrases),
          Object.keys(sourcePhrases),
        )

        if (deletePhrases.length) {
          console.log("Deleting phrases:", deletePhrases.join(", "))
          deletePhrases.forEach((phrase) => delete targetPhrases[phrase])
          await writeFile(targetFile, JSON.stringify(targetPhrases, null, 2))
        }

        const missingPhrases = difference(
          Object.keys(sourcePhrases),
          Object.keys(targetPhrases),
        )

        if (!missingPhrases.length) return

        // console.log("Translating phrases:", missingPhrases.join(", "))

        const runTranslation = async (key: string) => {
          const value = sourcePhrases[key] || ""
          const [translation] = await translateClient.translate(value, {
            from: "en",
            to: targetLanguage,
          })

          // Remove extra spaces to HTML added by Translation API
          targetPhrases[key] = translation.replaceAll(/\>\s/g, ">")
        }

        console.log("  Missing phrases:", missingPhrases.length)

        await bluebird.map(missingPhrases, runTranslation, {
          concurrency: CONCURRENCY,
        })

        await writeFile(targetFile, JSON.stringify(targetPhrases, null, 2))
      },
      { concurrency: CONCURRENCY },
    )
  })
}

main().catch((error) => console.error(error))
