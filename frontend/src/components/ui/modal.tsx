import type React from "react"

import { useEffect, useState } from "react"
import { createPortal } from "react-dom"
import Card from "@/components/ui/card"
import { IoClose } from "react-icons/io5";

interface ModalProps {
    isOpen: boolean
    onClose: () => void
    title?: string
    children: React.ReactNode
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)

        if (isOpen) {
            document.body.style.overflow = "hidden"
        }

        // Handle escape key press
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape") {
                onClose()
            }
        }

        window.addEventListener("keydown", handleEscape)

        return () => {
            document.body.style.overflow = "unset"
            window.removeEventListener("keydown", handleEscape)
        }
    }, [isOpen, onClose])

    const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget) {
            onClose()
        }
    }

    if (!mounted || !isOpen) return null

    return createPortal(
        <div
            className="fixed inset-0 z-[101] flex items-center justify-center bg-black/50 backdrop-blur-sm transition-all"
            onClick={handleBackdropClick}
            aria-modal="true"
            role="dialog"
        >
            <Card className="bg-white min-w-xl">
                <div onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center justify-between">
                        {title && <h2 className="text-xl font-semibold">{title}</h2>}
                        <button
                            onClick={onClose}
                            className="p-2 rounded-sm hover:bg-muted hover:cursor-pointer transition-colors duration-150"
                            aria-label="Close modal"
                        >
                            <IoClose className="h-4 w-4" />
                            <span className="sr-only">Close</span>
                        </button>
                    </div>
                    <div className="mt-4">{children}</div>
                </div>
            </Card>
        </div>,
        document.body,
    )
}
