import React, { ReactNode } from 'react';

interface SecondaryButtonProps {
  children: ReactNode;
  handler: () => void
  icon?: ReactNode;
  className?: string
  disabled?: boolean
}

const SecondaryButton: React.FC<SecondaryButtonProps> = ({ children, handler, icon, className, disabled = false }) => {
  return <button onClick={handler} disabled={disabled} className={`inline-flex items-center justify-center whitespace-nowrap rounded-lg px-4 text-sm font-medium ring-offset-bg shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus-ring focus-visible:ring-offset-2 disabled:pointer-events-none border border-ia-border bg-white text-ia-text hover:border-border-hover hover:bg-bg-subtle active:bg-bg-elevated active:border-border-hover disabled:border-border-disabled disabled:text-ia-text-disabled h-9 ml-auto transition-colors duration-150 hover:cursor-pointer ${className}`}>
    {icon}
    {children}
  </button>;
};

export default SecondaryButton;