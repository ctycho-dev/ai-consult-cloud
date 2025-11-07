import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Flex, Box, Text, Avatar, Tooltip } from "@mantine/core";
import { formatDistanceToNow } from "date-fns";
import { ru } from "date-fns/locale";
import { IoCopyOutline, IoWarningOutline } from "react-icons/io5";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "sonner";

import { Role, MessageStates } from "@/enums/enums";
import { IMessage } from "@/interfaces/message";
import { LoadingResponse } from "./loadingResponse";

interface MessageListProps {
  messages: IMessage[];
  sendMessage: (msg: string, resend?: boolean) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  sendMessage,
}) => {
  const [lastFailedTimeout, setLastFailedTimeout] = useState(false);
  const [lastFailedMessage, setLastFailedMessage] = useState<string>("");

  useEffect(() => {
    const last = messages.at(-1);
    if (last?.role === Role.USER && last.state === MessageStates.TIMEOUT) {
      setLastFailedTimeout(true);
      setLastFailedMessage(last.content as string);
    } else {
      setLastFailedTimeout(false);
      setLastFailedMessage("");
    }
  }, [messages]);

  const retrySending = () => {
    sendMessage(lastFailedMessage, true);
    setLastFailedMessage("");
  };

  const lastMessage = messages.at(-1);

  return (
    <Box pb="md">
      {messages.map((msg, i) => (
        <MessageItem
          key={msg.id}
          message={msg}
          isLast={i === messages.length - 1}
        />
      ))}

      {!!messages.length &&
        lastMessage?.role === Role.USER &&
        lastFailedTimeout &&
        !!lastFailedMessage && (
          <Flex
            justify="flex-start"
            align="flex-start"
            gap="md"
            mb="lg"
            maw="80%"
          >
            <Avatar color="blue" alt="AI" radius="xl">
              AI
            </Avatar>
            <div className="bg-muted p-3 px-4 rounded-radius border border-amber-500">
              <div className="flex items-center gap-2 text-amber-500 mb-2">
                <IoWarningOutline className="text-xl" />
                <span className="font-semibold text-sm">Request Timeout</span>
              </div>
              <div className="text-sm mb-3">
                Ассистент ИИ слишком долго отвечал. Это может быть связано с
                большим трафиком или сложным запросом.
              </div>
              <div className="flex gap-2">
                <button
                  onClick={retrySending}
                  className="justify-center whitespace-nowrap font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md px-3 h-8 text-xs flex items-center gap-1"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="lucide lucide-refresh-cw h-3 w-3"
                  >
                    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
                    <path d="M21 3v5h-5"></path>
                    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
                    <path d="M8 16H3v5"></path>
                  </svg>
                  <span>Повторить запрос</span>
                </button>
              </div>
            </div>
          </Flex>
        )}
    </Box>
  );
};

interface MessageItemProps {
  message: IMessage;
  isLast?: boolean;
}

const MessageItem: React.FC<MessageItemProps> = ({
  message,
  isLast = false,
}) => {
  const isUser = message.role === Role.USER;
  const state = message.state
  const role = message.role
  const sources = message.sources
  const content = message.content

  const showLoading =
    isLast &&
    role === Role.ASSISTANT &&
    state === MessageStates.PROCESSING &&
    content.trim() === "...";

  const getLocalTime = (utcDate: Date | string) => {
    return new Date(utcDate); // Let browser apply local timezone
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success("Скопировано.");
    } catch {
      toast.error("Failed to copy text");
    }
  };

  return (
    <>
      {showLoading ?
        <LoadingResponse />
        :
        <Flex
          justify={isUser ? "flex-end" : "flex-start"}
          align="flex-start"
          gap="md"
          mb="lg"
          style={isUser ? { marginLeft: "auto", maxWidth: '80%' } : {}}
        >
          {!isUser && (
            <Avatar color="blue" alt="AI" radius="xl">
              AI
            </Avatar>
          )}
          <Box className={`group flex flex-col ${isUser ? "items-end" : ""}`}>
            <div className={`${isUser ? 'bg-muted p-3 px-4 rounded-radius' : null}`}>
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {content.trim()}
                </ReactMarkdown>
              </div>
              {!isUser && sources && sources?.length > 0 && (
                <div className="mt-4 text-xs text-gray-600">
                  <div className="font-semibold mb-1">Источники:</div>
                  <ol className="list-decimal list-inside space-y-1">
                    {sources.map((src, index) => (
                      <li key={index}>
                        Файл: <strong><Link to={'/'} className="text-link">{src.file_name}</Link></strong>
                        {typeof src.page === "number" && src.page !== null
                          ? `, стр. ${src.page + 1}`
                          : null}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
            {isUser && message.created_at && (
              <div className="flex gap-x-2 items-center justify-between w-full">
                <div className="invisible opacity-0 group-hover:visible group-hover:opacity-100 transition-opacity duration-150">
                  <Tooltip label="Copy">
                    <button
                      type="button"
                      onClick={() => copyToClipboard(content)}
                      className="hover:bg-gray-100 p-1 rounded-md transition-colors duration-100"
                    >
                      <IoCopyOutline className="text-lg" />
                    </button>
                  </Tooltip>
                </div>
                <Text size="xs" c="dimmed">
                  {formatDistanceToNow(getLocalTime(message.created_at), {
                    locale: ru,
                    addSuffix: true,
                  })}
                </Text>
              </div>
            )}
          </Box>
        </Flex>
      }
    </>
  );
};
