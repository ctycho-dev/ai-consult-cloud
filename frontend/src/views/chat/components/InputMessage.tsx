import React from "react";
import { Link } from "react-router-dom";
import { FileButton } from "@mantine/core";
import { FaArrowUpLong } from "react-icons/fa6";
import { IoAttachSharp } from "react-icons/io5";

interface InputMessageProps {
  chatId: string
  value: string
  setValue: (msg: string) => void
  sendMessage: any
  handleKeyDown: (event: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  isDisabled: boolean
}

export const InputMessage: React.FC<InputMessageProps> = ({
  chatId,
  value,
  setValue,
  sendMessage,
  handleKeyDown,
  isDisabled
}) => {

  // const [cancelMessage] = useCancelMessageMutation()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    sendMessage()
  }

  const handleCancelSending = async () => {
    // try {
    //   setLoadingStates({ ...loadingStates, [chatId]: false });
    //   // await cancelMessage(chatId)
    // } catch (e) {
    //   console.log(e)
    // }
  }


  return (
    <form onSubmit={handleSubmit} className="relative flex flex-col w-full">
      <textarea
        disabled={isDisabled}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ask me anything..."
        className="w-full bg-sidebar-background p-4 rounded-2xl shadow-md resize-none outline-none placeholder-gray-500 text-gray-800"
        onKeyDown={handleKeyDown}
        rows={3}
      />
      <div className="absolute right-3 bottom-3 flex items-center gap-x-2">
        <div className="group flex items-center">
        
          <Link to={'/settings?tab=files'} className="p-0.5 group-hover:bg-slate-200 rounded-lg transition-all duration-150">
            <IoAttachSharp className="text-3xl text-slate-500" />
          </Link>
        </div>
        {
          isDisabled ?
            <button type="button" onClick={handleCancelSending} className={`bg-green-500 transition-all duration-150 rounded-full flex justify-center items-center w-8 h-8`}>
              <div className="bg-white h-2 w-2 z-10"></div>
            </button>
            :
            <button type="submit" className={`${value ? 'bg-green-500' : 'bg-slate-500'} transition-all duration-150 rounded-full flex justify-center items-center w-8 h-8`}>
              <FaArrowUpLong className="text-lg text-white" />
            </button>
        }
      </div>
    </form>
  )
}
