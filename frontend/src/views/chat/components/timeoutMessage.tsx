import { Flex, Avatar } from "@mantine/core";
import { IoWarningOutline } from "react-icons/io5";
import { useRetryMessageMutation } from "@/api/message";
import { IMessage } from '@/interfaces/message';


interface TimeoutMessageProps {
    message: IMessage
}

const TimeoutMessage: React.FC<TimeoutMessageProps> = ({ message }) => {
    const [retryMessage] = useRetryMessageMutation()

    return (
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
                          onClick={() => retryMessage(message.id)}
                        className="justify-center whitespace-nowrap font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md px-3 h-8 text-xs flex items-center gap-1 hover:cursor-pointer"
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
    )
}

export default TimeoutMessage