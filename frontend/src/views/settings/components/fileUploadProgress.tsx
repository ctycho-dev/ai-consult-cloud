import { FC, useState, useEffect } from 'react';
import { formatFileSize } from "@/utils"
import { FaRepeat } from "react-icons/fa6";
import { FileUpload } from "@/interfaces/file";


interface FileUploadProgressProps {
    data: FileUpload
    handleRepeatFileSending: any
}


export const FileUploadProgress: FC<FileUploadProgressProps> = ({ data, handleRepeatFileSending }) => {
    const [progress, setProgress] = useState(0);
    const [close, setClosed] = useState(false)

    useEffect(() => {
        const interval = setInterval(() => {
            setProgress(prev => {
                const newProgress = prev + Math.random() * 5;
                return newProgress > 90 ? 90 : newProgress;
            });
        }, 300);

        if (data.status == 'success' || data.status == 'error') {
            clearInterval(interval)
            setProgress(100)
        }

        return () => {
            clearInterval(interval)
        }
    }, [data]);


    const repeatRequest = () => {
        setProgress(0)
        handleRepeatFileSending(data)
    }

    return (
        <div>
            {!close &&
                <div className="mb-2">
                    <div className="bg-muted p-3 rounded-md">
                        <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    className="h-4 w-4"
                                >
                                    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path>
                                    <path d="M14 2v4a2 2 0 0 0 2 2h4"></path>
                                    <path d="M10 9H8"></path>
                                    <path d="M16 13H8"></path>
                                    <path d="M16 17H8"></path>
                                </svg>
                                <span className="font-medium text-sm">{data.file.name}</span>
                                <span className="text-xs text-muted-foreground">{formatFileSize(data.file.size)}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                {data.status == 'success' ? (
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="24"
                                        height="24"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        className="h-4 w-4 text-green-500"
                                    >
                                        <circle cx="12" cy="12" r="10"></circle>
                                        <path d="m9 12 2 2 4-4"></path>
                                    </svg>
                                ) : data.status == 'processing' ?
                                    (
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="24"
                                            height="24"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="2"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            className="lucide lucide-loader-circle h-4 w-4 animate-spin"
                                        >
                                            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                                        </svg>
                                    )
                                    : (
                                        <div className='flex gap-2 items-center'>
                                            <button onClick={repeatRequest}>
                                                <FaRepeat className='text-sm' />
                                            </button>
                                            <button onClick={() => { setClosed(true) }}>
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    width="24"
                                                    height="24"
                                                    viewBox="0 0 24 24"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    strokeWidth="2"
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    className="stroke-red-500 h-4 w-4"
                                                >
                                                    <path d="M18 6 6 18"></path>
                                                    <path d="m6 6 12 12"></path>
                                                </svg>
                                            </button>
                                        </div>
                                    )
                                }
                            </div>
                        </div>
                        <div
                            aria-valuemax={100}
                            aria-valuemin={0}
                            aria-valuenow={progress}
                            role="progressbar"
                            className="relative w-full overflow-hidden rounded-full h-1.5 bg-green-100"
                        >
                            <div
                                className={`h-full flex-1 transition-all ${data.status == 'processing' ? 'bg-gray-300' : data.status == 'success' ? 'bg-green-500' : 'bg-red-500'}`}
                                style={{ width: `${progress}%` }}
                            ></div>
                        </div>
                    </div>
                </div>
            }
        </div>
    )
}
