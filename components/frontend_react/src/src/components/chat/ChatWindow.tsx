import React, { useRef, useEffect } from "react"
import ChatInput from "./ChatInput"
import Expander from "@/components/Expander"
import { ChatContents } from "@/utils/types"
import Markdown from "react-markdown"
import rehypeRaw from "rehype-raw"

interface ChatWindowProps {
  onSubmit: (message: string) => void
  messages: ChatContents[]
  activeJob: boolean
}

const ChatWindow: React.FC<ChatWindowProps> = ({ onSubmit, messages, activeJob }) => {
  let index = 0
  const renderChat = (message: ChatContents) => {
    if (message.HumanInput) {
      return (
        <div key={index++}>
          <div className="flex items-center gap-6 pb-7 mx-2">
            <div className="i-material-symbols-face-outline color-info h-8 w-8 shrink-0 self-start"/>
            <div>
              {message.HumanInput}
            </div>
          </div>
        </div>
      )
    } else if (message.AIOutput) {
      return (
        <div key={index++}>
          <div className={`flex items-center gap-6 mx-2 pb-7}`}>
            <div className="i-logos-google-bard-icon h-8 w-8 shrink-0 self-start"/>
            <div>
              <Markdown children={message.AIOutput} rehypePlugins={[rehypeRaw]} />
            </div>
          </div>
        </div>
      )
    } else {
      return
    }
  }

  const endOfMessagesRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Scroll into view when activeJob is false
    if (activeJob) {
      endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" })
    }
    if (!messages[messages.length - 1].HumanInput && !activeJob) {
      endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, activeJob])

  return (
    <div className="flex flex-grow flex-col justify-between max-w-4xl">
      <div className="text-md flex-grow overflow-y-auto custom-scrollbar max-h-[calc(100vh-17.3rem)]">
        {messages.map(renderChat)}
        {activeJob && (
          <div className="flex items-center gap-6 pb-7 pt-2 mx-2">
            <div className="i-logos-google-bard-icon h-8 w-8 shrink-0 self-start loader ease-linear"/>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>
      <ChatInput onSubmit={onSubmit} activeJob={activeJob} />
    </div>
  )
}

export default ChatWindow