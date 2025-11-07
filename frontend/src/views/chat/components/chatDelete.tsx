import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Modal } from "@/components/ui/modal";
import { toast } from 'sonner'
import { useDeleteChatMutation } from "@/api/chat";
import PrimaryButton from "@/components/ui/primaryButton";
import SecondaryButton from "@/components/ui/secondaryButton";
import { IChatShort } from "@/interfaces/chat";

interface ChatDeleteProps {
    ws: IChatShort | null
    opened: boolean;
    close: () => void;
}


const ChatDelete: React.FC<ChatDeleteProps> = ({ ws, opened, close }) => {
    const navigate = useNavigate()
    const { workspaceId } = useParams<{ workspaceId?: string }>();
    const [isLoading, setIsLoading] = useState(false)

    const [deleteWorkspace] = useDeleteChatMutation()

    const handleCreate = async () => {
        if (!ws) return
        setIsLoading(true)

        try {
            const res = await deleteWorkspace(ws.id)
            if (res && 'data' in res) {
                toast.success('Рабочая область удалена.')
                if (ws.id == workspaceId) {
                    navigate('/')
                }
            } else {
                toast.error('Error')
            }
        } catch (e) {
            console.log(e)
            toast.error('Something went wrong.')
        } finally {
            close()
            setIsLoading(false)
        }
    }

    return (
        <Modal isOpen={opened} onClose={close} title="Переименовать рабочее пространство">
            <div className="mb-4 text-sm">
                <p>Вы уверены что хотите удалить рабочую область?</p>
            </div>
            <div className="flex justify-end">
                <div className="flex gap-2">
                    <SecondaryButton handler={close}>Отменить</SecondaryButton>
                    <PrimaryButton
                        type="button"
                        disabled={isLoading}
                        handler={handleCreate}
                    >Сохранить</PrimaryButton>
                </div>
            </div>
        </Modal>
    );
};

export default ChatDelete;
