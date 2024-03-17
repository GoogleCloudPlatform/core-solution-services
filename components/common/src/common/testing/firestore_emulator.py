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
"""
  Pytest Fixture for getting firestore emulator
"""
import os
import requests
import pytest

# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,line-too-long,useless-return,raise-missing-from

@pytest.fixture(scope="session", autouse=True)
def firestore_emulator():
  """
  Fixture to set up firestore emulator. Previous versions of this fixture
  would start and stop the emulator, but this was found to be very slow,
  and unreliable with the latest versions of the firestore emulator (13.5+).
  We now rely on the user to start the emulator prior to running tests with
  the following command:

  $ firebase emulators:start --only firestore --project fake-project &

  Once the emulator is started it can typically be left running without
  restarting.

  This fixture currently relies on the user to start the emulator outside
  the test run.

  Yields:
      None
  """
  # set env vars needed for emulator
  os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
  os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
  os.environ["PROJECT_ID"] = "fake-project"

  # clear database (and test that firestore emulator is running)
  try:
    requests.delete(
      "http://localhost:8080/emulator/v1/projects/fake-project/databases/(default)/documents",
      timeout=5)
  except:
    raise RuntimeError("Must start firestore emulator")

  # yield nothing as we are not creating any artifact
  yield None

  # no post-run cleanup needed - just return
  return


# pylint: disable = line-too-long
@pytest.fixture
def clean_firestore():
  """Fixture to clean data
  """
  requests.delete(
      "http://localhost:8080/emulator/v1/projects/fake-project/databases/(default)/documents",
      timeout=10)
