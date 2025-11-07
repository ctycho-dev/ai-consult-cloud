import React, { useState, useEffect, useMemo } from "react";
import {
    useGetStoragesQuery,
    useCreateStorageMutation,
    useDeleteStorageMutation,
    useUpdateStorageMutation
} from "@/api/storage";
import { useSelectStorageMutation } from "@/api/user";
import { IUserSelectStorage } from "@/interfaces/user";
import { IStorage, IStorageCreate } from "@/interfaces/storage";
import { useAuth } from "@/components/authProvider";
import { Button, Menu } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { toast } from 'sonner'
import { MdOutlineFileUpload } from "react-icons/md";
import { IconDownload, IconTrash, IconStar } from '@tabler/icons-react';
import { Modal } from "@/components/ui/modal";
import PrimaryButton from "@/components/ui/primaryButton";
import SecondaryButton from "@/components/ui/secondaryButton";
import { SiHomeassistant } from "react-icons/si";
import { InputField } from './inputFiled'; // typo? should be inputField

interface TabStorageProps { }

export const TabStorge: React.FC<TabStorageProps> = () => {
    const { user } = useAuth();

    // single active vs id from user profile
    const userVsId = getUserVectorStoreId(user)

    // optimistic UI state
    const [activeVsId, setActiveVsId] = useState<string | null>(null);

    // Loading states for individual actions
    const [loadingStates, setLoadingStates] = useState<{ [key: string]: boolean }>({});


    useEffect(() => {
        if (user) setActiveVsId(userVsId);
    }, [user]);


    // Storage state
    const [storages, setStorages] = useState<IStorage[]>([]);
    const { data, refetch } = useGetStoragesQuery();
    const [createStorage] = useCreateStorageMutation();
    const [updateStorage] = useUpdateStorageMutation();
    const [deleteStorage] = useDeleteStorageMutation();

    // Modals
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [storageName, setStorageName] = useState('');
    const [isCreating, setIsCreating] = useState(false);

    // Delete modal
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [selectedStorageId, setSelectedStorageId] = useState<string | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);
    const [selectStorage] = useSelectStorageMutation();


    useEffect(() => {
        if (data) setStorages(data)
    }, [data]);

    // Handle create storage
    const handleCreateStorage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!storageName) return;
        setIsCreating(true);
        try {
            const payload: IStorageCreate = {
                name: storageName
            }
            const res = await createStorage(payload);
            if (res && 'data' in res && res.data) {
                toast.success('Хранилище создано');
                // setStorages(prev => [...prev, res.data]);
                setIsCreateModalOpen(false);
                setStorageName('');
                refetch()
            } else if ('error' in res && res.error.data) {
                toast.error(res.error.data.detail || 'Ошибка при создании');
            }
        } catch (err) {
            toast.error('Ошибка при создании');
        }
        setIsCreating(false);
    };

    // Handle set as default
    const handleSetAsDefault = async (storageId: string) => {
        setLoadingStates(prev => ({ ...prev, [storageId]: true }));
        try {
            const res = await updateStorage({
                id: storageId,
                data: { default: true }
            });

            if (res && 'data' in res) {
                toast.success('Хранилище установлено по умолчанию');
                refetch(); // Refresh the list to show updated default status
            } else if ('error' in res) {
                const errorData = res.error as any;
                toast.error(errorData?.data?.detail || 'Ошибка при установке по умолчанию');
            }
        } catch (err) {
            toast.error('Ошибка при установке по умолчанию');
        }
        setLoadingStates(prev => ({ ...prev, [storageId]: false }));
    };

    const handleConfirmDelete = async () => {
        if (!selectedStorageId) return;
        setIsDeleting(true);
        try {
            const res = await deleteStorage(selectedStorageId);
            if (res && 'data' in res) {
                toast.success('Хранилище удалено');
                // setStorages(prev => prev.filter(item => item.id !== selectedStorageId));
                setIsDeleteModalOpen(false);
                setSelectedStorageId(null);
                refetch()
            } else {
                toast.error('Ошибка при удалении');
            }
        } catch (err) {
            toast.error('Ошибка при удалении');
        }
        setIsDeleting(false);
    };

    // For UI: Dummy download click handler
    const handleDownloadClick = (item: IStorage) => {
        toast.info("Загрузка не реализована");
    }

    const handleSelectStorage = async (vsId: string) => {

        const payload: IUserSelectStorage = {
            user_id: null,
            vs_id: vsId

        }
        const res = await selectStorage(payload).unwrap();
        console.log(res);
        if (res) {
            toast.success("Хранилище выбрано.");
            setActiveVsId(getUserVectorStoreId(res));
        } else if ('error' in res) {
            const error = res.error as any;
            console.log(error)
            toast.error('Произошла ошибка при выборе ассистента.');
        }
    }

    return (
        <div className="border border-border rounded-md bg-card p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold mb-1">Хранилище</h2>
                <Button
                    variant="filled"
                    color="green"
                    onClick={() => setIsCreateModalOpen(true)}
                >
                    <MdOutlineFileUpload className="text-xl mr-2" />
                    <span>Создать хранилище</span>
                </Button>
            </div>

            <table className="w-full caption-bottom text-sm">
                <thead>
                    <tr className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Название</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Создано</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-right">Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {storages.map(item => {
                        return (
                            <tr className={`border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted ${activeVsId == item.vector_store_id ? 'bg-gray-100' : ''}`} key={item.id}>
                                <td className="p-4 align-middle">
                                    <div className="flex gap-2">
                                        {item.name}
                                        {item.default && (
                                            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                                По умолчанию
                                            </span>
                                        )}
                                    </div>
                                </td>
                                <td className="p-4 align-middle">{item.created_at.split('T')[0]}</td>
                                <td className="p-4 align-middle text-right relative">
                                    <Menu shadow="md" width={250}>
                                        <Menu.Target>
                                            <button className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 w-10" type="button">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>
                                            </button>
                                        </Menu.Target>
                                        <Menu.Dropdown>
                                            <Menu.Label>Действия</Menu.Label>
                                            <Menu.Item
                                                leftSection={<SiHomeassistant size={14} />}
                                                onClick={() => { handleSelectStorage(item.vector_store_id) }}
                                            >
                                                Выбрать
                                            </Menu.Item>
                                            {!item.default && (
                                                <Menu.Item
                                                    leftSection={<IconStar size={14} />}
                                                    onClick={() => handleSetAsDefault(item.id)}
                                                    disabled={loadingStates[item.id]}
                                                >
                                                    {loadingStates[item.id] ? 'Установка...' : 'Установить по умолчанию'}
                                                </Menu.Item>
                                            )}
                                            <Menu.Item
                                                color="red"
                                                leftSection={<IconTrash size={14} />}
                                                onClick={() => {
                                                    setSelectedStorageId(item.id);
                                                    setIsDeleteModalOpen(true);
                                                }}
                                            >
                                                Удалить
                                            </Menu.Item>
                                        </Menu.Dropdown>
                                    </Menu>
                                </td>
                            </tr>
                        )
                    })}
                </tbody>
            </table>

            <Modal
                title="Новое хранилище"
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
            >
                <form onSubmit={handleCreateStorage} className="space-y-4">
                    <InputField
                        id="storageName"
                        label="Название"
                        type="text"
                        value={storageName}
                        onChange={e => setStorageName(e.target.value)}
                        required
                    />
                    <div className="flex justify-end gap-2">
                        <SecondaryButton handler={() => setIsCreateModalOpen(false)}>
                            Отмена
                        </SecondaryButton>
                        <PrimaryButton type="submit" disabled={!storageName || isCreating}>
                            Создать
                        </PrimaryButton>
                    </div>
                </form>
            </Modal>


            <Modal title="Удалить хранилище" isOpen={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)}>
                <div className="mb-4 text-sm">
                    <p>Вы уверены что хотите удалить это хранилище?</p>
                </div>
                <div className="flex justify-end gap-2">
                    <SecondaryButton handler={() => setIsDeleteModalOpen(false)}>
                        Отмена
                    </SecondaryButton>
                    <PrimaryButton
                        type="button"
                        disabled={isDeleting}
                        handler={handleConfirmDelete}
                    >
                        Удалить
                    </PrimaryButton>
                </div>
            </Modal>

        </div>
    );
};


function getUserVectorStoreId(user: any): string | null {
    return user?.tools?.find((t: any) => t?.type === "file_search")?.vector_store_ids?.[0] ?? user?.vector_store_id ?? null;
}