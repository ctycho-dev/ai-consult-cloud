import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { IUser } from "../interfaces/user.ts";
import { useVerifyUserMutation, useLogoutUserMutation } from "@/api/user.ts";
import { chatApi } from "@/api/chat.ts";
import { fileApi } from "@/api/file.ts";
import { settingsApi } from "@/api/settings.ts";
import { useDispatch } from "react-redux";


interface AuthContextProps {
    user: IUser | null
    isAuthenticated: boolean
    isLoading: boolean
    login: (token: string) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const dispatch = useDispatch()
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [user, setUser] = useState<IUser | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [verifyUser] = useVerifyUserMutation();
    const [logoutUser] = useLogoutUserMutation()
    const navigate = useNavigate();


    useEffect(() => {
        const handleVerifyUser = async () => {
            try {
                const res = await verifyUser().unwrap();
                setUser(res)
                setIsAuthenticated(true);
            } catch (err) {
                // console.error('Verification error:', err);
                navigate('/login');
            } finally {
                setIsLoading(false); // Ensure loading state is updated
            }
        };

        handleVerifyUser();
    }, [verifyUser, navigate]);

    const login = () => {
        setIsAuthenticated(true);
    };

    const logout = async () => {
        await logoutUser()
        setUser(null);
        setIsAuthenticated(false);
        dispatch(fileApi.util.resetApiState());
        dispatch(chatApi.util.resetApiState());
        dispatch(settingsApi.util.resetApiState());
        navigate('/login');
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextProps => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
