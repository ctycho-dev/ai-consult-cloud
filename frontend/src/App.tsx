import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/components/authProvider.tsx';
import Layout from '@/components/layout/appLayout.tsx';
import Login from '@/views/login/login.tsx';
import Home from '@/views/home/home.tsx';
import ChatView from '@/views/chat/chat';
import SettingsView from '@/views/settings/settings.tsx';


function App(): React.ReactNode {

    return (
        <Router>
            <AuthProvider>
                <Routes>
                    <Route path="/" element={<Layout />}>
                        <Route index element={<Home />} />
                        <Route path="/chat/:chatId" element={<ChatView />} />
                        <Route path="/settings" element={<SettingsView />} />
                    </Route>
                    <Route path="/login" element={<Login />} />
                </Routes>
            </AuthProvider>
        </Router>
    );
}

export default App
