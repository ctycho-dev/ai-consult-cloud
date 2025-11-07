import React, { useEffect, useState, useRef } from "react";
import { Avatar } from '@mantine/core';
import { useAuth } from "../authProvider";

import { FiUser, FiLogOut } from "react-icons/fi";

interface ProfileProps {

}

export const Profile: React.FC<ProfileProps> = ({ }) => {
    const { user, logout } = useAuth();
    const [opened, setOpened] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null);
    const openBtn = useRef<HTMLDivElement>(null);

    const handleClickOutside = (event: MouseEvent) => {
        if (
            dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
            openBtn.current && !openBtn.current.contains(event.target as Node)
        ) {
            setOpened(false);
        }
    };

    useEffect(() => {
        if (opened) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [opened]);

    return (
        <div className='relative py-2'>
            <div ref={openBtn} className='p-2 hover:bg-accent rounded-radius flex gap-2 items-center text-sm' onClick={() => setOpened(!opened)}>
                <Avatar></Avatar>
                <span>{user?.email}</span>
            </div>
            {opened &&
                <div
                    ref={dropdownRef}
                    className='bg-white absolute bottom-16 border-border border shadow-md rounded-radius left-0 right-0'>
                    <div className='py-3 px-4 border-b border-border text-md font-semibold'>Профиль</div>
                    <div className='py-3 px-4 flex items-center gap-2 border-b border-border font-medium'>
                        <FiUser />
                        <span className="text-sm whitespace-nowrap overflow-hidden overflow-ellipsis min-w-0 flex-1">
                            {user?.email}
                        </span>
                    </div>
                    <button className='py-3 px-4 flex items-center gap-2 w-full hover:cursor-pointer' onClick={logout}>
                        <FiLogOut />
                        <span className="text-sm">Log out</span>
                    </button>
                </div>
            }
        </div>
    )
}