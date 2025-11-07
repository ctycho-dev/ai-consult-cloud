import React, { useState, useEffect } from "react";
import { Input } from '@mantine/core';
import { Modal } from "@/components/ui/modal"
import { toast } from 'sonner'
import { useUpdateChatMutation } from "@/api/chat";
import PrimaryButton from "@/components/ui/primaryButton";
import SecondaryButton from "@/components/ui/secondaryButton";
import { IChatShort } from "@/interfaces/chat";

interface ChatUpdateProps {
    ws: IChatShort | null
    opened: boolean;
    close: () => void;
}


const ChatUpdate: React.FC<ChatUpdateProps> = ({ ws, opened, close }) => {
    const [newName, setNewName] = useState('');

    const [updateWorkspace] = useUpdateChatMutation()


    useEffect(() => {
        if (ws) setNewName(ws.name)
    }, [ws])


    const handleCreate = async () => {
        if (!ws) return

        if (newName.trim() == '') {
            toast.error('Название не соответствует требованиям.')
            close()
            return
        }

        try {
            // const res = await updateWorkspace({
            //     name: newName,
            //     id: ws.id
            // })
            // if (res && 'data' in res) {
            //     toast.success('Рабочая область обновлена.')
            //     close()
            // } else {
            //     toast.error('Error')
            // }
        } catch (e) {
            console.log(e)
            toast.error('Something went wrong.')
        } finally {
            close()
            setNewName('')
        }

    }

    return (
        <Modal isOpen={opened} onClose={close} title="Переименовать рабочее пространство">
            <div className="mb-4">
                <Input.Wrapper label="Название">
                    <Input
                        value={newName}
                        onChange={(e) => { setNewName(e.target.value) }}
                    />
                </Input.Wrapper>
            </div>
            <div className="flex justify-end">
                <div className="flex gap-2">
                    <SecondaryButton handler={close}>Отменить</SecondaryButton>
                    <PrimaryButton
                        type="button"
                        disabled={!newName}
                        handler={handleCreate}
                    >Сохранить</PrimaryButton>
                </div>
            </div>
        </Modal>
    );
};

export default ChatUpdate;
