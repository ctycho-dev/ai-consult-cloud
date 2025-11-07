import React, { useState, useEffect } from "react";
import { Button, Select, Menu } from '@mantine/core';
import { toast } from 'sonner'
import {
    useGetUsersQuery,
    useCreateUserMutation,
    useDeleteUserMutation
} from "@/api/user";
import {
    useGetStoragesQuery,
} from "@/api/storage";
import { IStorage } from "@/interfaces/storage";
import { IUser } from '@/interfaces/user'
import { useAuth } from "@/components/authProvider";
import { Role } from "@/enums/enums";
import { InputField } from './inputFiled'
import {
    IconTrash
} from '@tabler/icons-react';
import { IoMdAdd } from "react-icons/io";
import { Modal } from "@/components/ui/modal";
import PrimaryButton from "@/components/ui/primaryButton";
import SecondaryButton from "@/components/ui/secondaryButton";


interface TabUsersProps { }


export const TabUsers: React.FC<TabUsersProps> = ({ }) => {
    const { user } = useAuth();
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
    const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false)
    const { data } = useGetUsersQuery()
    const { data: storages } = useGetStoragesQuery();

    const [deleteUser] = useDeleteUserMutation()
    // const [selectAgent] = useSelectAgentMutation()

    const [users, setUsers] = useState<IUser[] | []>([]);
    const [email, setEmail] = useState('')
    const [role, setRole] = useState<string | null>(null)
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [isDisabled, setButtonDisabled] = useState(true)
    const [selectedUser, setSelectedUser] = useState<string | null>(null)
    const [createUser] = useCreateUserMutation()

    useEffect(() => {
        const savedEmail = localStorage.getItem('newUserEmail');
        const savedRole = localStorage.getItem('newUserRole');

        if (savedEmail) setEmail(savedEmail);
        if (savedRole) setRole(savedRole);
    }, []);

    useEffect(() => {
        if (data) setUsers(data)
    }, [data])

    useEffect(() => {
        if (email && password && confirmPassword) {
            setButtonDisabled(false)
        }
    }, [email, password, confirmPassword])

    // Helper function to get user's storage
    const getUserStorage = (userTools: any[]): IStorage | null => {
        if (!userTools || !storages) return null;
        
        // Find file_search tool in user's tools
        const fileSearchTool = userTools.find(tool => tool.type === "file_search");
        if (!fileSearchTool || !fileSearchTool.vector_store_ids || fileSearchTool.vector_store_ids.length === 0) {
            return null;
        }
        
        // Get the first vector store ID
        const vectorStoreId = fileSearchTool.vector_store_ids[0];
        
        // Find matching storage
        return storages.find(storage => storage.vector_store_id === vectorStoreId) || null;
    };

    const handleSubmit = async (e: any) => {
        e.preventDefault()

        if (password != confirmPassword) {
            toast.error('Пароли не совпадают.')
            return
        }
        setButtonDisabled(true)

        const res = await createUser({
            email,
            password,
            ...(role && { role: role as string })
        })

        if (res && 'data' in res && res.data) {
            toast.success('Good.')
            setUsers((prev) => [...prev, res.data]);

            setEmail('');
            setRole('');
            localStorage.removeItem('newUserEmail');
            localStorage.removeItem('newUserRole');
        } else if ('error' in res) {
            const error = res.error as any;

            if (error.status === 409) {
                toast.error('Такой пользователь уже существует.');
            } else if (error.data && error.data.detail) {
                toast.error(error.data.detail);
            } else {
                toast.error('Произошла ошибка при создании пользователя.');
            }
        }
        setIsCreateModalOpen(false)
        setPassword('')
        setConfirmPassword('')
        setButtonDisabled(false)
    }

    const handleDeleteClick = (fileId: string) => {
        setSelectedUser(fileId)
        setIsConfirmModalOpen(true)
    }

    const handleConfirmDelete = async () => {
        if (!selectedUser) return;

        try {
            const res = await deleteUser(selectedUser);
            if (res && 'data' in res) {
                toast.success('Пользователь успешно удалён');
                setUsers(prev => prev.filter(user => user.id !== selectedUser));

            } else {
                toast.error('Что-то пошло не так');
            }
        } catch (error) {
            toast.error('Ошибка при удалении файла');
        } finally {
            setIsConfirmModalOpen(false)
            setSelectedUser(null);
        }
    };

    // const handleAgentChange = async (userId: string, agentId: string) => {
    //     // Adjust this payload if your mutation is different
    //     const payload: IUserSelectAgent = {
    //         user_id: userId,
    //         agent_id: agentId
    //     }

    //     const res = await selectAgent(payload);
    //     if (res && 'data' in res) {
    //         toast.success('Ассистент выбран.');
    //         setUsers((prev) =>
    //             prev.map(u => u.id === userId ? { ...u, agent: agents?.find(a => a.id === agentId) ?? null } : u)
    //         );
    //     } else {
    //         toast.error('Произошла ошибка при выборе ассистента.');
    //     }
    // }

    return (
        <div className="border border-border rounded-md bg-card p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Пользовательский менеджер</h2>
                <Button variant="filled" color="green" onClick={() => setIsCreateModalOpen(true)} className="mb-2"><IoMdAdd className="text-xl mr-2" />Создать пользователя</Button>
            </div>
            <table className="w-full caption-bottom text-sm">
                <thead className="[&amp;_tr]:border-b">
                    <tr className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0">Почта</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0">Роль</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0">Хранилище</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0">Создан</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0 text-right">Действия</th>
                    </tr>
                </thead>
                <tbody className="[&amp;_tr:last-child]:border-0">
                    {users.map((u) => {
                        const userStorage = getUserStorage(u.tools || []);

                        return (
                            <tr key={u.id} className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                <td className="p-4 align-middle [&amp;:has([role=checkbox])]:pr-0">{u.email}</td>
                                <td className="p-4 align-middle [&amp;:has([role=checkbox])]:pr-0">{u.role}</td>
                                <td className="p-4 align-middle [&amp;:has([role=checkbox])]:pr-0">
                                    {userStorage ? (
                                        <div className="flex items-center gap-2">
                                            <span>{userStorage.name}</span>
                                            {userStorage.default && (
                                                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                                    По умолчанию
                                                </span>
                                            )}
                                        </div>
                                    ) : (
                                        <span className="text-gray-500 italic">Не выбрано</span>
                                    )}
                                </td>
                                {/* {user?.role === Role.ADMIN && (
                                    <td className="p-4 align-middle">
                                        <Select
                                            value={u.agent?.id || null}
                                            onChange={(agentId) => handleAgentChange(u.id, agentId!)}
                                            placeholder="Выбрать ассистента"
                                            data={(agents ?? []).map(a => ({
                                                value: a.id,
                                                label: a.name
                                            }))}
                                            clearable
                                        />
                                    </td>
                                )} */}
                                <td className="p-4 align-middle [&amp;:has([role=checkbox])]:pr-0">{u.created_at.split('T')[0]}</td>
                                <td className="p-4 align-middle [&amp;:has([role=checkbox])]:pr-0 text-right relative">
                                    <Menu shadow="md" width={150}>
                                        <Menu.Target>
                                            <button className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&amp;_svg]:pointer-events-none [&amp;_svg]:size-4 [&amp;_svg]:shrink-0 hover:bg-accent hover:text-accent-foreground h-10 w-10" type="button" id="radix-«r1u»" aria-haspopup="menu" aria-expanded="false" data-state="closed">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>
                                            </button>
                                        </Menu.Target>

                                        <Menu.Dropdown>
                                            <Menu.Label>Действия</Menu.Label>
                                            <Menu.Item
                                                color="red"
                                                leftSection={<IconTrash size={14} />}
                                                onClick={() => { handleDeleteClick(u.id) }}
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
            <Modal title="Удалить пользователя" isOpen={isConfirmModalOpen} onClose={() => setIsConfirmModalOpen(false)}>
                <div className="mb-4 text-sm">
                    <p>Вы уверены что хотите удалить пользователя?</p>
                </div>
                <div className="flex justify-end">
                    <div className="flex gap-2">
                        <SecondaryButton handler={close}>Отменить</SecondaryButton>
                        <PrimaryButton
                            type="button"
                            handler={handleConfirmDelete}
                        >Сохранить</PrimaryButton>
                    </div>
                </div>
            </Modal>
            <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Новый пользователь">
                <form action="#" method="POST" className="space-y-4" onSubmit={handleSubmit}>
                    {
                        user?.role == Role.ADMIN ?
                            <>
                                <div>
                                    <Select
                                        label="Role"
                                        placeholder="Pick value"
                                        data={[Role.ADMIN, Role.USER]}
                                        color="green"
                                        value={role}
                                        onChange={setRole}
                                    />
                                </div>
                            </>
                            : null
                    }
                    <InputField
                        id="email"
                        label="Email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />

                    <InputField
                        id="password"
                        label="Password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />

                    <InputField
                        id="confirm-password"
                        label="Confirm Password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                    <PrimaryButton type="submit" disabled={isDisabled}>Создать</PrimaryButton>
                </form>
            </Modal>
        </div>
    )
}