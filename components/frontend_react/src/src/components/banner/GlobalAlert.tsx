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

interface GlobalAlertProps {}
import { alertStore } from "@/store"
import { classNames } from "@/utils/dom"
import { ALERT_TYPE } from "@/utils/types"
import {
  ExclamationCircleIcon,
  InformationCircleIcon,
  HandThumbUpIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline"

const GlobalAlert: React.FC<GlobalAlertProps> = () => {
  const alert = alertStore((state) => state.alert)
  const setAlert = alertStore((state) => state.setAlert)

  if (!alert) return <></>
  if (alert.closeable === false && !alert.durationMs) {
    console.warn("Alert will always stay open")
  }

  const alertType =
    alert.type === ALERT_TYPE.SUCCESS
      ? "success"
      : alert.type === ALERT_TYPE.WARNING
      ? "warning"
      : alert.type === ALERT_TYPE.ERROR
      ? "error"
      : "info"

  const IconComponent =
    alertType === "success"
      ? HandThumbUpIcon
      : alertType === "error"
      ? ExclamationCircleIcon
      : alertType === "warning"
      ? ExclamationCircleIcon
      : InformationCircleIcon

  return (
    <div
      data-testid="global-alert"
      className={classNames(
        "alert w-full bg-opacity-75 p-3 shadow-lg",
        `alert-${alertType}`,
      )}
    >
      {/* Hidden span to ensure all potentially used classes are not purged */}
      <span className="alert-info alert-success alert-warning alert-error hidden text-error-content text-warning-content text-success-content text-info-content"></span>

      <div className="flex items-center justify-between">
        <div className="mr-2 flex flex-row items-center">
          <IconComponent className="mr-3 w-6 shrink-0" />
          <div data-testid="global-alert-message">{alert.message}</div>
        </div>

        <div
          data-testid="global-alert-close"
          onClick={() => setAlert(null)}
          className={classNames(
            "group cursor-pointer rounded-md bg-base-100 bg-opacity-0 transition hover:bg-opacity-20",
            alert.closeable === false ? "hidden" : "",
          )}
        >
          <XCircleIcon
            className={classNames(
              "m-1 w-6 shrink-0 opacity-75 transition group-hover:opacity-100",
              `text-${alertType}-content`,
            )}
          />
        </div>
      </div>
    </div>
  )
}

export default GlobalAlert
