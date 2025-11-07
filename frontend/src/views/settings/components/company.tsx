import React, { useState, useEffect } from "react";
import { useDisclosure } from '@mantine/hooks';
import { Menu, Button, Select, Input } from '@mantine/core';
import { toast } from 'sonner'
import {
    useGetCompaniesQuery,
    useDeleteCompanyMutation,
    useCreateCompanyMutation
} from "@/api/company";
import { 
    useGetWorkspacesQuery 
} from "@/api/workspace";
import { Modal } from "@/components/ui/modal";
import { ICompany } from '@/interfaces/company'
import { categories } from "@/enums";
import SecondaryButton from "@/components/ui/secondaryButton";
import PrimaryButton from "@/components/ui/primaryButton";
import { IoMdAdd } from "react-icons/io";
import {
    IconTrash
} from '@tabler/icons-react';


interface CompanyProps {
}


export const Company: React.FC<CompanyProps> = ({ }) => {
    const { refetch: refetchWorkspaces } = useGetWorkspacesQuery();
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
    const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false)
    const { data, refetch } = useGetCompaniesQuery()

    const [companies, setCompanies] = useState<ICompany[] | []>([]);
    const [name, setName] = useState('')
    const [category, setCategory] = useState<string | null>(null);
    const [isDisabled, setButtonDisabled] = useState(true)
    const [createCompany] = useCreateCompanyMutation()
    const [deleteCompany, { error: errorDelete }] = useDeleteCompanyMutation()
    const [selectedCompany, setSelectedCompany] = useState<string | null>(null)


    useEffect(() => {
        if (data) {
            setCompanies(data)
        }
    }, [data])

    useEffect(() => {
        if (name && category) {
            setButtonDisabled(false)
        }
    }, [name, category])

    useEffect(() => {
        if (errorDelete) {
            // Type guard to check if this is a FetchBaseQueryerrorDelete
            if ('status' in errorDelete) {
                if (errorDelete.status === 403) {
                    toast.error('Forbidden.')
                } else if (errorDelete.status === 429) {
                    toast.error('Slow down')
                } else if (errorDelete.status === 500) {
                    toast.error('Something went wrong')
                } else {
                    toast.error('Login failed')
                }
            } else {
                // Handle other types of errors (like SerializedError)
                toast.error('Login failed')
            }
        }
    }, [errorDelete])

    const handleSubmit = async (e: any) => {
        e.preventDefault()
        if (!name || !category) {
            toast.error('Fille all fields.')
            return
        }

        setButtonDisabled(true)

        const res = await createCompany({ name, category })
        if (res && 'data' in res && res.data) {
            toast.success('Good.')
            setCompanies((prev) => [...prev, res.data]);
            await refetchWorkspaces()
        }
        else if (res && 'error' in res && 'status' in res.error && res.error.status == 409) {
            toast.error('Такой пользователь существует.')
        } else {
            toast.error('Что то пошло не так, попробуйте снова через пару минут.')
        }
        setIsCreateModalOpen(false)
        setButtonDisabled(false)
        await refetch()
    }

    const handleDeleteClick = (fileId: string) => {
        setSelectedCompany(fileId)
        setIsConfirmModalOpen(true)
    }

    const handleConfirmDelete = async () => {
        if (!selectedCompany) return;

        try {
            await deleteCompany(selectedCompany).unwrap()
            toast.success('Компания успешно удалена');

            await refetch();
            await refetchWorkspaces()
        } finally {
            setIsConfirmModalOpen(false)
            setSelectedCompany(null);
        }
    };

    return (
        <div className="border border-border rounded-md bg-card p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Менеджер компаний</h2>
                <Button variant="filled" color="green" onClick={() => setIsCreateModalOpen(true)} className="mb-2"><IoMdAdd className="text-xl mr-2" />Создать компанию</Button>
            </div>
            <table className="w-full caption-bottom text-sm">
                <thead className="[&amp;_tr]:border-b">
                    <tr className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0">Название</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0">Категория</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0">Создан</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground [&amp;:has([role=checkbox])]:pr-0 text-right">Действия</th>
                    </tr>
                </thead>
                <tbody className="[&amp;_tr:last-child]:border-0">
                    {companies.map((company) => {
                        return (
                            <tr key={company.id} className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                <td className="p-4 align-middle [&amp;:has([role=checkbox])]:pr-0">{company.name}</td>
                                <td className="p-4 align-middle [&amp;:has([role=checkbox])]:pr-0">{company.category}</td>
                                <td className="p-4 align-middle [&amp;:has([role=checkbox])]:pr-0">{company.created_at.split('T')[0]}</td>
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
                                                onClick={() => { handleDeleteClick(company.id) }}
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
            <Modal title="Удалить файл" isOpen={isConfirmModalOpen} onClose={() => setIsConfirmModalOpen(false)}>
                <div className="mb-4 text-sm">
                    <p>Вы уверены что хотите удалить файл?</p>
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
            <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Новая компания">
                <form action="#" method="POST" className="space-y-4" onSubmit={handleSubmit}>
                    <div>
                        <Input.Wrapper label="Название">
                            <Input
                                id="name"
                                name="name"
                                type="text"
                                required
                                autoComplete="name"
                                value={name}
                                onChange={(e) => { setName(e.target.value) }}
                            />
                        </Input.Wrapper>
                    </div>
                    <div>
                        <Select
                            label="Категория"
                            placeholder="Выберите категорию"
                            data={categories}
                            color="green"
                            onChange={setCategory}
                        />
                    </div>
                    <PrimaryButton type="submit" disabled={isDisabled}>Создать</PrimaryButton>
                </form>
            </Modal>
        </div>
    )
}