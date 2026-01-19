import React, { useState, useEffect } from "react";
import {
    useGetStoragesQuery,
    useCreateStorageMutation,
    useDeleteStorageMutation,
    useUpdateStorageMutation
} from "@/api/storage";
import { Role } from "@/enums/enums";
import { useSelectStorageMutation } from "@/api/user";
import { useGetStatsQuery } from "@/api/file";
import { IUserSelectStorage } from "@/interfaces/user";
import { IStorage, IStorageCreate } from "@/interfaces/storage";
import { useAuth } from "@/components/authProvider";
import { Button, Menu, Badge, Tooltip } from '@mantine/core';
import { toast } from 'sonner'
import { MdOutlineFileUpload } from "react-icons/md";
import { IconTrash, IconStar } from '@tabler/icons-react';
import { Modal } from "@/components/ui/modal";
import PrimaryButton from "@/components/ui/primaryButton";
import SecondaryButton from "@/components/ui/secondaryButton";
import { InputField } from './inputFiled';

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
        console.log("Fetched storages:", data);
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

    const handleConfirmDelete = async () => {
        if (!selectedStorageId) return;
        setIsDeleting(true);
        try {
            const res = await deleteStorage(selectedStorageId);
            if (res && 'data' in res) {
                toast.success('Хранилище удалено');
                refetch()
            } else if ('error' in res) {
                const errorData = res.error as any;
                toast.error(errorData?.data?.detail || 'Ошибка при удалении');
            }
        } catch (err) {
            toast.error('Ошибка при удалении');
        } finally {
            setIsDeleteModalOpen(false);
            setSelectedStorageId(null);
            setIsDeleting(false);
        }
    };

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
                {user?.role == Role.ADMIN &&
                    <Button
                        variant="filled"
                        color="green"
                        onClick={() => setIsCreateModalOpen(true)}
                    >
                        <MdOutlineFileUpload className="text-xl mr-2" />
                        <span>Создать хранилище</span>
                    </Button>
                }
            </div>

            <table className="w-full caption-bottom text-sm">
                <thead>
                    <tr className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Название</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Бот</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">S3</th>
                        {/* <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Vector Store ID</th> */}
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Статистика</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Создано</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-right">Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {storages.map(item => {
                        return (
                            <tr className={`border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted ${activeVsId == item.vectorStoreId ? 'bg-gray-100' : ''}`} key={item.id}>
                                <td className="p-4 align-middle">
                                    <div className="flex gap-2">
                                        {item.name}
                                    </div>
                                </td>
                                <td className="p-4 align-middle">{item.botName}</td>
                                <td className="p-4 align-middle">{item.s3Bucket}</td>
                                <td className="p-4 align-middle">
                                    <StorageStats vectorStoreId={item.vectorStoreId} />
                                </td>
                                <td className="p-4 align-middle">{item.createdAt.split('T')[0]}</td>
                                <td className="p-4 align-middle text-right relative">
                                    <Menu shadow="md" width={250}>
                                        <Menu.Target>
                                            <button className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 w-10" type="button">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>
                                            </button>
                                        </Menu.Target>
                                        <Menu.Dropdown>
                                            <Menu.Label>Действия</Menu.Label>
                                            {/* <Menu.Item
                                                leftSection={<SiHomeassistant size={14} />}
                                                onClick={() => { handleSelectStorage(item.vectorStoreId) }}
                                            >
                                                Выбрать
                                            </Menu.Item> */}
                                            {user?.role == Role.ADMIN &&
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
                                            }
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
    return user?.tools?.find((t: any) => t?.type === "file_search")?.vectorStoreIds?.[0] ?? user?.vectorStoreId ?? null;
}


const StorageStats: React.FC<{ vectorStoreId: string }> = ({ vectorStoreId }) => {
    const { data: stats, isLoading, error } = useGetStatsQuery(vectorStoreId);

    if (isLoading) {
        return <span className="text-xs text-muted-foreground">Загрузка...</span>;
    }

    if (error || !stats) {
        return <span className="text-xs text-red-500">Ошибка</span>;
    }

    const hasErrors = (stats.upload_failed + stats.delete_failed) > 0;
    const isProcessing = stats.indexing > 0 || stats.stored > 0 || stats.deleting > 0;

    return (
        <div className="flex flex-col gap-1 text-xs">
            <div className="flex gap-2 items-center">
                <Tooltip label="Всего файлов">
                    <Badge size="sm" color="gray" variant="light">
                        {stats.total}
                    </Badge>
                </Tooltip>
                <Tooltip label="Проиндексировано">
                    <Badge size="sm" color="green" variant="light">
                        ✓ {stats.indexed}
                    </Badge>
                </Tooltip>
                {isProcessing && (
                    <Tooltip label={`Индексируется: ${stats.indexing}, В очереди: ${stats.stored}, Удаляется: ${stats.deleting}`}>
                        <Badge size="sm" color="blue" variant="light">
                            ⏳ {stats.indexing + stats.stored + stats.deleting}
                        </Badge>
                    </Tooltip>
                )}
                {hasErrors && (
                    <Tooltip label={`Ошибок загрузки: ${stats.upload_failed}, Ошибок удаления: ${stats.delete_failed}`}>
                        <Badge size="sm" color="red" variant="light">
                            ✗ {stats.upload_failed + stats.delete_failed}
                        </Badge>
                    </Tooltip>
                )}
            </div>
        </div>
    );
};