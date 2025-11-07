import React, { useRef, useState, useEffect } from "react"
import { Link } from "react-router-dom";
import { MdOutlineFileUpload } from "react-icons/md";
import { FaRegFile } from "react-icons/fa";

interface ChatHeaderProps {
    name: string
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({ name }) => {
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
        <div className="fixed top-0 left-0 right-0 mb-2 z-10 text-xl font-bold">
            <div className="ml-[260px] px-4 h-16 flex items-center justify-between">
                <span>{name}</span>
                <div className="relative">
                    <Link to={'/settings?tab=files'} className="rounded-radius shadow-sm hover:shadow-md duration-150 transition-shadow border border-border font-semibold px-4 py-2 flex gap-2 items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-folder-open h-4 w-4"><path d="m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2"></path></svg>
                        <span className="text-sm">Файлы</span>
                    </Link>

                </div>
            </div>
        </div>
    )
}