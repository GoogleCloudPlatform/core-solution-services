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

import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryParams } from "@/utils/routing"

interface IconProps {
  iconClass: string
  onClick: () => void
  active: boolean
  tooltip: string
}

interface IconBarProps {
  chatId: string | null
}

const Icon: React.FC<IconProps> = ({ iconClass, onClick, active, tooltip }) => {
  return (
    <div data-tip={tooltip} className="tooltip tooltip-secondary tooltip-bottom" data-placement="bottom">
    <button
      onClick={onClick}
      className={"flex justify-center items-center p-2 rounded-full group hover:bg-base-200 transition"}
    >
      <i className={`${iconClass} ${active ? 'text-info' : 'text-base-content/75'} group-hover:text-base-content/100 transition h-6 w-6 shrink-0`}></i>
    </button></div>
  )
}

const IconBar: React.FC<IconBarProps> = ({ chatId }) => {
  const [activeIcon, setActiveIcon] = useState<string | null>(null)
  const [paramCleared, setParamCleared] = useState(false)
  const [chatIdHolder, setChatIdHolder] = useState<string | null>(null)
  const handleIconClick = (iconName: string) => {
    // If the clicked icon is already active, deactivate it (optional behavior)
    if (activeIcon === iconName) {
      setActiveIcon(null)
    } else {
      setActiveIcon(iconName)
    }
  }


  const navigate = useNavigate()
  const params = useQueryParams()

  const handleRefresh = () => {
    setChatIdHolder(chatId)
    navigate("?", { replace: false })
    setParamCleared(true)
  }

  useEffect(() => {
    if (chatIdHolder !== null) {
      params.set("chat_id", chatIdHolder)
    } else {
      let currentId = params.get("chat_id")
      currentId && params.set("chat_id", currentId)
    }
    const newQueryString = params.toString()

    navigate(`?${newQueryString}`, { replace: false })
  }, [paramCleared, navigate])

  return (
    <div className="flex items-center gap-2 px-4 w-fit ml-7">
      <Icon 
        iconClass="i-material-symbols-thumb-up-outline-rounded" 
        onClick={() => handleIconClick("like")} 
        active={activeIcon === "like"}
        tooltip="Good response"
      />
      <Icon 
        iconClass="i-material-symbols-thumb-down-outline-rounded" 
        onClick={() => handleIconClick("dislike")} 
        active={activeIcon === "dislike"}
        tooltip="Bad response"
      />
      <Icon 
        iconClass="i-material-symbols-share-outline" 
        onClick={() => handleIconClick("share")} 
        active={activeIcon === "share"}
        tooltip="Share & export"
      />
      <Icon 
        iconClass="i-material-symbols-g-translate" 
        onClick={() => handleIconClick("translate")} 
        active={activeIcon === "translate"}
        tooltip="Translate response"
      />
      <Icon 
        iconClass="i-material-symbols-info-outline" 
        onClick={() => handleIconClick("info")} 
        active={activeIcon === "info"}
        tooltip="Get more info"
      />
      <Icon 
        iconClass="i-material-symbols-refresh-rounded" 
        onClick={() => handleRefresh()} 
        active={activeIcon === "refresh"}
        tooltip="Reload chat"
      />
      <Icon 
        iconClass="i-material-symbols-more-vert" 
        onClick={() => handleIconClick("more")} 
        active={activeIcon === "more"}
        tooltip="More"
      />
    </div>
  )
}

export default IconBar
