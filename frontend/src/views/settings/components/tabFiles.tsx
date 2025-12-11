import React, { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from 'uuid';
import {
    useGetFilesQuery,
    useUploadFileMutation,
    useDeleteFileMutation,
    useDownloadFileMutation
} from "@/api/file";
import {
    useGetStoragesQuery
} from "@/api/storage";
import { useAuth } from "@/components/authProvider";
import { Button, FileButton, Menu, TextInput, Switch } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IFile } from '@/interfaces/file';
import { toast } from 'sonner';
import { FileUploadProgress } from "./fileUploadProgress";
import { MdOutlineFileUpload } from "react-icons/md";
import { FileUpload } from "@/interfaces/file";
import { FileState, Role } from "@/enums/enums";
import { formatFileSize } from "@/utils";
import { FileIcon } from "./fileIcon";
import {
    IconDownload,
    IconTrash,
    IconSearch
} from '@tabler/icons-react';
import { IUser } from "@/interfaces/user.ts";
import { Modal } from "@/components/ui/modal";
import PrimaryButton from "@/components/ui/primaryButton";
import SecondaryButton from "@/components/ui/secondaryButton";

interface GloblaFileProps { }

export const GloblaFile: React.FC<GloblaFileProps> = () => {
    const { user } = useAuth();
    const [opened, { open, close }] = useDisclosure(false);
    const [uploadedFiles, setUploadedFiles] = useState<FileUpload[]>([]);
    const [files, setFiles] = useState<IFile[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const { data } = useGetFilesQuery();
    const [deleteFile] = useDeleteFileMutation();
    const [uploadFile] = useUploadFileMutation();
    const [downloadFile] = useDownloadFileMutation();
    const [selectedFileId, setSelectedFileId] = useState<number | null>(null);
    const resetRef = useRef<() => void>(null);

    const { data: storages } = useGetStoragesQuery();

    // Create map: vectorStoreId → storage name
    const storageMap = React.useMemo<Record<string, string>>(() => {
        if (!storages) return {};
        const map: Record<string, string> = {};
        storages.forEach(s => {
            map[s.vector_store_id] = s.name;
        });
        return map;
    }, [storages]);

    // Update upload status
    const setResponse = (fileId: string, status: FileUpload['status']) => {
        setUploadedFiles(prev =>
            prev.map(file =>
                file.id === fileId ? { ...file, status } : file
            )
        );
    };

    // Handle file upload
    const handleUploadFile = async (selectedFiles: File[] | null) => {
        if (!user?.id || !selectedFiles || selectedFiles.length === 0) return;

        await Promise.all(
            selectedFiles.map(async (file) => {
                const fileId = uuidv4();
                const newFile: FileUpload = {
                    id: fileId,
                    file,
                    status: 'processing'
                };

                setUploadedFiles(prev => [...prev, newFile]);
                await handleFileSending(newFile);
            })
        );
    };

    const handleFileSending = async (data: FileUpload) => {
        try {
            setIsLoading(true);
            await uploadFile({ files: data.file }).unwrap();
            toast.success('Файл успешно загружен');
            setResponse(data.id, 'success');
        } catch (error: any) {
            const errorMsg = error?.data?.detail || 'Ошибка загрузки файла';
            toast.error(errorMsg);
            setResponse(data.id, 'error');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRepeatFileSending = (data: FileUpload) => {
        setResponse(data.id, 'processing');
        handleFileSending(data);
    };

    // Confirm delete dialog
    const handleDeleteClick = (fileId: number) => {
        setSelectedFileId(fileId);
        open();
    };

    const handleConfirmDelete = async () => {
        if (!selectedFileId) return;

        try {
            setIsLoading(true);
            await deleteFile(selectedFileId).unwrap();
            toast.success('Файл успешно удалён');
            setFiles(prev => prev.filter(file => file.id !== selectedFileId));
        } catch (error: any) {
            const errorMsg = error?.data?.detail || 'Ошибка при удалении файла';
            toast.error(errorMsg);
        } finally {
            close();
            setSelectedFileId(null);
            setIsLoading(false);
        }
    };

    // Update files when API data changes
    useEffect(() => {
        if (data) setFiles(data);
    }, [data]);

    // Filter files - Simplified for hard delete
    const filteredFiles = files.filter(file => {
        const matchesSearch = !searchTerm ||
            file.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            file.id.toString().includes(searchTerm);

        return matchesSearch;
    });

    // Simplified download handler - no blob handling needed
    const handleDownloadFile = async (fileId: number, fileName: string) => {
        try {
            setIsLoading(true);
            toast.info('Начинается загрузка файла...');

            // This now handles everything internally and returns void
            await downloadFile(fileId).unwrap();

            toast.success('Файл успешно загружен');
        } catch (error: any) {
            const errorMsg = error?.data?.detail || 'Ошибка при загрузке файла';
            toast.error(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="border border-border rounded-md bg-card p-4">
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-4">
                <div>
                    <h2 className="text-xl font-semibold mb-1">Файловый менеджер</h2>
                    <div className="text-xs text-muted-foreground">
                        Загрузка файлов может занимать до 3 минут на один файл
                    </div>
                </div>
                {user && user.role != Role.USER &&
                    <FileButton resetRef={resetRef} onChange={handleUploadFile} multiple>
                        {(props) => (
                            <Button
                                loading={isLoading}
                                loaderProps={{ type: 'dots' }}
                                variant="filled"
                                color="green"
                                {...props}
                                className=""
                            >
                                <MdOutlineFileUpload className="text-xl mr-2" />
                                <span>Загрузить файл</span>
                            </Button>
                        )}
                    </FileButton>
                }
            </div>

            {/* Search only - no active filter needed for hard delete */}
            <div className="flex flex-col sm:flex-row gap-3 mb-4 items-start sm:items-center">
                <TextInput
                    placeholder="Поиск по названию или ID..."
                    leftSection={
                        <IconSearch
                            size={16}
                            style={{
                                color: '#999',
                                pointerEvents: 'none'
                            }}
                        />
                    }
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.currentTarget.value)}
                    styles={{
                        input: {
                            paddingLeft: '2.5rem',
                            paddingRight: '1rem'
                        }
                    }}
                    style={{ flex: 1, maxWidth: '400px' }}
                />
            </div>

            {/* Uploading Files Progress */}
            {uploadedFiles.length > 0 && (
                <div className="mb-4">
                    {uploadedFiles.map(item => (
                        <FileUploadProgress
                            key={`${item.id}-${item.file.lastModified}`}
                            data={item}
                            handleRepeatFileSending={handleRepeatFileSending}
                        />
                    ))}
                </div>
            )}

            {/* Files Table */}
            <table className="w-full caption-bottom text-sm">
                <thead className="[&_tr]:border-b">
                    <tr className="border-b border-border hover:bg-muted/50">
                        <th className="h-12 px-4 text-left font-medium text-muted-foreground">Название</th>
                        <th className="h-12 px-4 text-left font-medium text-muted-foreground">Размер</th>
                        <th className="h-12 px-4 text-left font-medium text-muted-foreground">Хранилище</th>
                        <th className="h-12 px-4 text-left font-medium text-muted-foreground">Создано</th>
                        <th className="h-12 px-4 text-right font-medium text-muted-foreground">Действия</th>
                    </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                    {filteredFiles.length === 0 ? (
                        <tr>
                            <td colSpan={5} className="p-4 text-center text-muted-foreground">
                                {files.length === 0 ? 'Файлы не найдены' : 'Нет файлов по фильтру'}
                            </td>
                        </tr>
                    ) : (
                        filteredFiles.map(item => {
                            const storageName = storageMap[item.vectorStoreId];
                            return (
                                <FileItem
                                    key={item.id}
                                    user={user}
                                    item={item}
                                    onDeleteClick={handleDeleteClick}
                                    onDownloadClick={handleDownloadFile}
                                    isLoading={isLoading}
                                    storageName={storageName}
                                />
                            );
                        })
                    )}
                </tbody>
            </table>

            {/* Delete Confirmation Modal */}
            <Modal title="Удалить файл" isOpen={opened} onClose={close}>
                <div className="mb-4 text-sm">
                    <p>Вы уверены, что хотите удалить файл?</p>
                    {files.find(f => f.id === selectedFileId)?.lastDeleteError && (
                        <p className="text-orange-600 mt-2 text-xs">
                            Ошибка: {files.find(f => f.id === selectedFileId)?.lastDeleteError}
                        </p>
                    )}
                </div>
                <div className="flex justify-end">
                    <div className="flex gap-2">
                        <SecondaryButton handler={close}>Отменить</SecondaryButton>
                        <PrimaryButton
                            type="button"
                            disabled={isLoading}
                            handler={handleConfirmDelete}
                        >
                            Удалить
                        </PrimaryButton>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

// ----------------------------
// FileItem Component
// ----------------------------
interface FileItemProps {
    user: IUser | null
    item: IFile;
    onDeleteClick: (fileId: number) => void;
    onDownloadClick: (fileId: number, fileName: string) => void;
    isLoading: boolean
    storageName?: string;
}

const FileItem: React.FC<FileItemProps> = ({ 
    user, item, onDeleteClick, onDownloadClick, isLoading, storageName 
}) => {
    const getStatusColor = (status: FileState) => {
        switch (status) {
            case FileState.PENDING: return "bg-gray-100 text-gray-800";
            case FileState.UPLOADING:
            case FileState.INDEXING: return "bg-blue-100 text-blue-800";
            case FileState.STORED: return "bg-yellow-100 text-yellow-800";
            case FileState.INDEXED: return "bg-green-100 text-green-800";
            case FileState.FAILED: return "bg-red-100 text-red-800";
            default: return "bg-gray-100 text-gray-800";
        }
    };

    const getStatusLabel = (status: FileState) => {
        switch (status) {
            case FileState.PENDING: return "Ожидает";
            case FileState.UPLOADING: return "Загрузка";
            case FileState.STORED: return "Сохранён";
            case FileState.INDEXING: return "Индексируется";
            case FileState.INDEXED: return "Готов";
            case FileState.FAILED: return "Ошибка";
            default: return "Неизв.";
        }
    };

    const canDownload = item.status === FileState.STORED || item.status === FileState.INDEXED;

    return (
        <tr className="border-b border-border transition-colors hover:bg-muted/50">
            <td className="p-4 align-middle">
                <div className="flex items-center gap-3">
                    <FileIcon contentType={item.contentType ? item.contentType : ''} />
                    <div>
                        <div className="font-medium">{item.name}</div>
                    </div>
                </div>
            </td>
            <td className="p-4 align-middle">{item.size ? formatFileSize(item.size) : ''}</td>
            <td className="p-4">{storageName || "—"}</td>
            <td className="p-4 align-middle">
                {item.createdAt
                    ? (() => {
                        try {
                            const date = new Date(item.createdAt);
                            return isNaN(date.getTime()) ? '—' : date.toISOString().split('T')[0];
                        } catch {
                            return '—';
                        }
                    })()
                    : '—'}
            </td>
            <td className="p-4 align-middle text-right">
                <Menu shadow="md" width={200}>
                    <Menu.Target>
                        <button
                            disabled={isLoading}
                            className="inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 hover:bg-accent hover:text-accent-foreground h-10 w-10 disabled:opacity-50"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="1" />
                                <circle cx="19" cy="12" r="1" />
                                <circle cx="5" cy="12" r="1" />
                            </svg>
                        </button>
                    </Menu.Target>
                    <Menu.Dropdown>
                        <Menu.Label>Действия</Menu.Label>
                        <Menu.Item
                            leftSection={<IconDownload size={14} />}
                            disabled={!canDownload || isLoading}
                            onClick={() => canDownload && onDownloadClick(item.id, item.name || 'file')}
                        >
                            Скачать
                        </Menu.Item>
                        {user && user.role != Role.USER && 
                            <Menu.Item
                                color="red"
                                leftSection={<IconTrash size={14} />}
                                disabled={isLoading}
                                onClick={() => onDeleteClick(item.id)}
                            >
                                Удалить
                            </Menu.Item>
                        }
                    </Menu.Dropdown>
                </Menu>

                {/* Status Badge */}
                <div className="mt-1 flex justify-end">
                    <span
                        className={`inline-flex text-xs font-medium px-2.5 py-0.5 rounded-full ${getStatusColor(
                            item.status
                        )}`}
                        title={item.lastError || undefined}
                    >
                        {getStatusLabel(item.status)}
                    </span>
                </div>
            </td>
        </tr>
    );
};
