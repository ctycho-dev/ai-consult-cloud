import { useEffect, useState, useRef } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Toaster } from 'sonner';
import { Tooltip } from '@mantine/core';
import { useAppSelector } from '@/hooks/app';

import { Profile } from './profile.tsx';
import { useGetChatsByUserQuery } from '@/api/chat.ts';
import ChatCreate from '@/views/chat/components/chatCreate.tsx';
import ChatUpdate from '@/views/chat/components/chatUpdate.tsx';
import ChatDelete from '@/views/chat/components/chatDelete.tsx';

import { IChatShort } from '@/interfaces/chat.ts';

import { HiDotsHorizontal } from 'react-icons/hi';
import { RiDeleteBin5Line } from 'react-icons/ri';
import { MdDriveFileRenameOutline } from 'react-icons/md';
import { LuBrain } from "react-icons/lu";
import { IoSettingsOutline } from "react-icons/io5";


export function Navbar() {
    const { chats } = useAppSelector((state) => state.chats);
    const { } = useGetChatsByUserQuery()

    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
    const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false)
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
    const [openDropdownId, setOpenDropdownId] = useState<string | null>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const openBtn = useRef<HTMLDivElement>(null);

    const [chosenWorkspace, setChosenWorkspace] = useState<IChatShort | null>(null)
    const { chatId } = useParams<{ chatId?: string }>();

    const handleDropdown = (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        setOpenDropdownId(openDropdownId === id ? null : id);
    };

    const handleClickOutside = (event: MouseEvent) => {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
            setOpenDropdownId(null);
        }
    };

    useEffect(() => {
        if (openDropdownId !== null) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [openDropdownId]);


    const workspaceAction = (type: string, ws: IChatShort) => {
        setChosenWorkspace(ws)
        if (type === 'update') {
            setIsUpdateModalOpen(true)
        } else if (type === 'delete') {
            setIsDeleteModalOpen(true)
        }
        setOpenDropdownId(null)
    };

    return (
        <>
            <div className="bg-sidebar-background absolute top-0 bottom-0 right-0 left-0 flex flex-col">
                <div className='p-4'>
                    <Link to={'/'} className='flex items-center gap-2'>
                        <div className='bg-black p-1 w-max'><LuBrain className='text-white text-[24px]' /></div>
                        <div className='font-bold text-xl'>Assistant Cloud</div>
                    </Link>
                </div>
                <div className='mx-2 h-[1px] bg-sidebar-border'></div>
                <div className='p-2'>
                    <Link to={'/'} className={`p-2 ${!chatId ? 'bg-sidebar-accent' : ''} hover:bg-sidebar-accent rounded-radius flex gap-2 items-center font-medium text-base`}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
                        <span>Главная</span>
                    </Link>
                </div>
                <div className='mx-2 h-[1px] bg-sidebar-border'></div>
                <div className='p-2'>
                    <div className='flex items-center justify-between p-2 text-sidebar-foreground/70'>
                        <span className='text-sm'>Рабочее пространство</span>
                        <button className='rounded-md hover:bg-accent w-5 h-5 flex justify-center items-center' onClick={() => setIsCreateModalOpen(true)}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 stroke-accent-foreground"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>
                        </button>
                    </div>
                </div>
                <div className='flex flex-col h-full'>
                    <div className='p-2 flex-1 overflow-scroll'>
                        <ul className='grid gap-1'>
                            {chats?.map((chat) => (
                                <li
                                    key={`chat-${chat.id}`}
                                    className={`${chatId == chat.id ? 'bg-sidebar-accent' : ''} w-full relative group p-2 hover:bg-sidebar-accent rounded-md`}
                                >
                                    <Tooltip label={chat.name}>
                                        <Link to={`/chat/${chat.id}`} className="w-full flex justify-between items-center max-w-[220px]">
                                            <span className="flex-grow overflow-hidden whitespace-nowrap text-ellipsis">{chat.name}</span>
                                        </Link>
                                    </Tooltip>
                                    <div ref={openBtn} onClick={(e) => handleDropdown(e, chat.id)} className="absolute right-2 top-1/2 -translate-y-1/2">
                                        <button type="button" className="invisible group-hover:visible flex justify-center items-center p-1 rounded-lg bg-[#f9fbff] h-7 w-7">
                                            <HiDotsHorizontal className="z-10" />
                                        </button>
                                    </div>
                                    {openDropdownId === chat.id && (
                                        <div ref={dropdownRef} className="z-20 absolute right-0 mt-2 rounded-md bg-white border border-border">
                                            <div className="py-1">
                                                <button
                                                    onClick={() => workspaceAction('update', chat)}
                                                    className="flex items-center gap-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-sidebar-accent hover:cursor-pointer"
                                                >
                                                    <MdDriveFileRenameOutline className="text-xl" />
                                                    <span className='text-sm'>Переименовать</span>
                                                </button>
                                                <button
                                                    onClick={() => workspaceAction('delete', chat)}
                                                    className="flex items-center gap-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-sidebar-accent hover:cursor-pointer"
                                                >
                                                    <RiDeleteBin5Line className="text-xl" />
                                                    <span className='text-sm'>Удалить</span>
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className='px-4'>
                        <div className='mb-4'>
                            <Link
                                to={'/settings'}
                                className="p-2 flex items-center gap-2 hover:bg-accent rounded-radius w-full text-sm"
                            >
                                <IoSettingsOutline className="text-xl" />
                                <span>Настройки</span>
                            </Link>
                        </div>
                        <div className='h-[1px] bg-sidebar-border'></div>
                        <Profile />
                    </div>
                </div>
            </div>

            <ChatCreate opened={isCreateModalOpen} close={() => setIsCreateModalOpen(false)} />
            <ChatUpdate
                ws={chosenWorkspace}
                opened={isUpdateModalOpen}
                close={() => setIsUpdateModalOpen(false)}
            />
            <ChatDelete
                ws={chosenWorkspace}
                opened={isDeleteModalOpen}
                close={() => setIsDeleteModalOpen(false)}
            />
            <Toaster richColors />
        </>
    );
}