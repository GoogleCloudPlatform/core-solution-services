# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" build script for query engines """

#pylint: disable=wrong-import-position

import asyncio
import logging
import sys
sys.path.append("../components/llm_service/src")
sys.path.append("../components/common/src")
from services.query.query_service import query_engine_build

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

async def main(doc_url, query_engine, user_id):
  print(f"*** building query index for {doc_url}," \
        f" query_engine {query_engine}, for user id {user_id}")

  q_engine, docs_processed, docs_not_processed = \
      await query_engine_build(doc_url, query_engine, user_id)
  print(f"*** docs_processed {docs_processed}")
  print(f"*** docs__not_processed {docs_not_processed}")

if __name__ == "__main__":
  args = sys.argv[1:]

  doc_url = args[0]
  query_engine = args[1]
  user_id = args[2]

  asyncio.get_event_loop().run_until_complete(
        main(doc_url, query_engine, user_id))
