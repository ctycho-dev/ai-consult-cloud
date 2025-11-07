import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import {
    useGetMessagesQuery,
    useCreateMessageMutation
} from "@/api/message";
import { useGetChatByIdQuery } from "@/api/chat";
import { MessageStates, Role } from "@/enums/enums.ts";
import { IMessage } from '@/interfaces/message';
import { InputMessage } from '@/views/chat/components/InputMessage';
import { MessageList } from '@/views/chat/components/messageList';
import { ScrollArea } from "@mantine/core";
import { toast } from "sonner";
import { ChatHeader } from '@/views/chat/components/chatHeader';
import { useAuth } from "@/components/authProvider.tsx";

interface IMessageState {
    [key: string]: string;
}

interface IFailedSendingChat {
    [key: string]: boolean;
}

const ChatView = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const { chatId } = useParams<{ chatId?: string }>();
    const [inputMessages, setMessage] = useState<IMessageState>({});
    const [messages, setMessages] = useState<IMessage[]>([]);
    const [chatFailedSending, setChatFailedSending] = useState<IFailedSendingChat>({});
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const { data, refetch, isError, error } = useGetMessagesQuery(chatId as string, {
        skip: !chatId,
    });
    const [createMessage] = useCreateMessageMutation();
    const { data: chat, isLoading: chatLoaded } = useGetChatByIdQuery(chatId as string, {
        skip: !chatId,
    });

    useEffect(() => {
        if (chatLoaded && !chat) {
            navigate('/');
        }
    }, [chat, chatLoaded]);

    // Re-fetch messages on mount/chat switch
    useEffect(() => {
        if (chatId) refetch();
    }, [chatId, refetch]);

    // Setup SSE for real-time updates
    useEffect(() => {
        if (!chatId) return;
        const source = new EventSource(`/api/v1/message/sse/${chatId}`);

        source.onopen = () => {
            console.log("✅ SSE connection established");
        };

        source.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("🔥 SSE Message:", data);
                upsertMessage(data);
            } catch (err) {
                console.error("Failed to parse SSE message:", err);
            }
        };

        source.onerror = (err) => {
            console.warn("SSE connection error:", err);
        };

        return () => source.close();
    }, [chatId, location]);

    // Handle 404 chat not found
    useEffect(() => {
        if (isError && 'status' in (error as FetchBaseQueryError)) {
            const fetchError = error as FetchBaseQueryError;
            if (fetchError.status === 404) {
                navigate('/');
                toast.error('Chat not found');
            }
        }
    }, [isError, error, navigate]);

    useEffect(() => {
        if (data) setMessages(data);
    }, [data]);

    // Auto scroll to latest message
    useEffect(() => {
        setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 200);
    }, [messages]);

    const addMessage = (message: IMessage[]) => {
        setMessages((prev) => [...prev, ...message]);
    };

    const upsertMessage = (newMessage: IMessage) => {
        setMessages((prevMessages) => {
            const index = prevMessages.findIndex(m => m.id === newMessage.id);
            if (index !== -1) {
                const updated = [...prevMessages];
                updated[index] = newMessage;
                return updated;
            } else {
                return [...prevMessages, newMessage];
            }
        });
    };

    const handleMessage = async (msg: string, resend = false) => {
        if (!chatId || !msg || !user) return;

        const lastMessage = messages[messages.length - 1];
        if (lastMessage?.state === MessageStates.PROCESSING) {
            toast.warning("Дождитесь получения ответа.");
            return;
        }

        if (!resend) {
            setMessage({ ...inputMessages, [chatId]: '' });
        }

        setChatFailedSending({ ...chatFailedSending, [chatId]: false });

        try {
            const res = await createMessage({ chat_id: chatId, content: msg }).unwrap();
            if (!res) {
                toast.error('Что-то пошло не так.');
                return;
            }
            addMessage(res);
        } catch (error) {
            // Try to extract specific error message
            // Try different shapes of the error object
            const err = error as any; // <--- THIS
            let message = "Ошибка при отправке.";
            if (err?.data?.detail) message = err.data.detail;
            else if (err?.data?.message) message = err.data.message;
            else if (err?.message) message = err.message;

            toast.error(message);
            setChatFailedSending({ ...chatFailedSending, [chatId]: true });
        }
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (chatId && event.key === 'Enter') {
            event.preventDefault();
            handleMessage(inputMessages[chatId]);
        }
    };

    // 👇 NEW: Check if assistant is still processing
    const isAssistantProcessing =
        messages.length > 0 &&
        messages[messages.length - 1].role === Role.ASSISTANT &&
        messages[messages.length - 1].state === MessageStates.PROCESSING;

    return (
        <>
            {chatId &&
                <div className="w-full h-screen flex flex-col">
                    <ChatHeader name="Chat" />
                    <div className="flex-1 flex flex-col max-w-3xl w-full mx-auto mt-6">
                        <ScrollArea style={{ flex: 1 }}>
                            <MessageList
                                sendMessage={handleMessage}
                                messages={messages}
                            />
                            <div ref={messagesEndRef} />
                        </ScrollArea>
                        <div className="bg-white sticky bottom-0 z-10 pb-2">
                            <div className="flex flex-col gap-2">
                                <InputMessage
                                    key={`input-${chatId}`}
                                    chatId={chatId}
                                    value={inputMessages[chatId]}
                                    setValue={(msg: string) => setMessage({ ...inputMessages, [chatId]: msg })}
                                    sendMessage={() => handleMessage(inputMessages[chatId])}
                                    handleKeyDown={handleKeyDown}
                                    isDisabled={isAssistantProcessing}
                                />
                                <div className="text-center text-gray-600 text-xs">AI ассистент может ошибаться.</div>
                            </div>
                        </div>
                    </div>
                </div>
            }
        </>
    );
};

export default ChatView;
