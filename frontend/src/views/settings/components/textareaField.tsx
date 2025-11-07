// Add this below your InputField component

interface TextareaFieldProps {
    id: string;
    label: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    required?: boolean;
    readOnly?: boolean;
    rows?: number;
}

export const TextareaField: React.FC<TextareaFieldProps> = ({
    id, label, value, onChange, required, readOnly = false, rows = 3
}) => (
    <div>
        <label htmlFor={id} className="block text-sm/6 font-medium text-gray-900">
            {label}
        </label>
        <div className="mt-2">
            <textarea
                id={id}
                value={value}
                onChange={onChange}
                disabled={readOnly}
                required={required}
                rows={rows}
                className="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-[#2e7d32] sm:text-sm/6 disabled:bg-gray-100 resize-y"
            />
        </div>
    </div>
);
