import React, { ReactNode } from 'react';

interface PrimaryButtonProps {
   type?: "button" | "submit" | "reset" | undefined
   children: ReactNode;
   handler?: () => void
   icon?: ReactNode;
   className?: string
   disabled?: boolean
}

const PrimaryButton: React.FC<PrimaryButtonProps> = ({ type = 'button', children, handler, icon, className, disabled = false }) => {
   return (
      <button 
         type={type}
         onClick={handler} 
         disabled={disabled} 
         className={`text-white text-sm font-semibold disabled:pointer-events-none bg-interactive hover:bg-interactive-hover hover:cursor-pointer disabled:bg-bg-disabled disabled:text-ia-text-disabled px-3 h-9 rounded-lg transition-colors duration-150 ${className}`}>
         {icon}
         {children}
      </button>
   )
};

export default PrimaryButton;