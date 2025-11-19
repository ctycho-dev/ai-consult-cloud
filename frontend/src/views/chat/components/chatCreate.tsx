import React, { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Input } from '@mantine/core';
import { toast } from 'sonner';
import {
    useCreateChatMutation,
} from "@/api/chat.ts";
import { useAuth } from "@/components/authProvider.tsx";
import PrimaryButton from "@/components/ui/primaryButton";
import SecondaryButton from "@/components/ui/secondaryButton";

interface ChatCreateProps {
    opened: boolean;
    close: () => void;
}

const ChatCreate: React.FC<ChatCreateProps> = ({ opened, close }) => {
    const { user } = useAuth();
    const [chatName, setChatName] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);

    const [createChat] = useCreateChatMutation();

    const handleCreate = async () => {
        if (!user) return;
        setIsLoading(true);

        try {
            const res = await createChat({
                name: chatName,
            });

            if (res && 'data' in res && res.data) {
                toast.success('Рабочая область создана.');
                setChatName('');
            } else {
                toast.error('Произошла неизвестная ошибка.');
            }
        } catch (error: any) {
            toast.error(error?.message || 'Произошла ошибка при отправке запроса.');
        } finally {
            close();
            setIsLoading(false);
        }
    };

    return (
        <Modal isOpen={opened} onClose={close} title="Создать новый чат">
            <div className="mb-4">
                <Input.Wrapper label="Название">
                    <Input
                        value={chatName}
                        onChange={(e) => setChatName(e.target.value)}
                    />
                </Input.Wrapper>
            </div>
            <div className="flex justify-end">
                <div className="flex gap-2">
                    <SecondaryButton handler={close}>Отменить</SecondaryButton>
                    <PrimaryButton
                        type="button"
                        disabled={!chatName || isLoading}
                        handler={handleCreate}
                    >
                        Сохранить
                    </PrimaryButton>
                </div>
            </div>
        </Modal>
    );
};

export default ChatCreate;
