interface InputFieldProps {
    id: string;
    label: string;
    type: string;
    value: string;
    readOnly?: boolean
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    required?: boolean;
}

export const InputField: React.FC<InputFieldProps> = ({ id, label, type, value, onChange, required, readOnly = false }) => (
    <div>
        <label htmlFor={id} className="block text-sm/6 font-medium text-gray-900">
            {label}
        </label>
        <div className="mt-2">
            <input
                id={id}
                type={type}
                value={value}
                disabled={readOnly}
                onChange={onChange}
                required={required}
                className="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-[#2e7d32] sm:text-sm/6 disabled:bg-[#f1f3f5] disabled:opacity-60 disabled:pointer-events-none"
            />
        </div>
    </div>
);