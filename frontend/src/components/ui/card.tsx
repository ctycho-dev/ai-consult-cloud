import React, { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string
}

const Card: React.FC<CardProps> = ({ children, className }) => {
  return <div className={`px-6 py-5 border border-border rounded-2xl ${className}`}>{children}</div>;
};

export default Card;