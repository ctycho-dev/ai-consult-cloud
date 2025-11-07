interface FileIconProps {
    contentType: string
}

export const FileIcon: React.FC<FileIconProps> = ({ contentType }) => {
    const getColor = () => {
        if (contentType.includes('pdf')) return 'text-red-500';
        if (contentType.includes('excel') || contentType.includes('spreadsheet') || contentType.includes('xls')) return 'text-green-500';
        if (contentType.includes('word') || contentType.includes('docx') || contentType.includes('doc')) return 'text-blue-500';
        if (contentType.includes('powerpoint') || contentType.includes('ppt')) return 'text-orange-500';
        if (contentType.includes('image')) return 'text-purple-500';
        return 'text-gray-500';
    };

    return (
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
            className={`h-4 w-4 ${getColor()}`}>
            <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path>
            <path d="M14 2v4a2 2 0 0 0 2 2h4"></path>
            <path d="M10 9H8"></path>
            <path d="M16 13H8"></path>
            <path d="M16 17H8"></path>
        </svg>
    )
}