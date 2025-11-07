import { Outlet } from 'react-router-dom';
import { Navbar } from "./navbar.tsx";
import { AppShell } from "@mantine/core";

const Layout = ({ }) => {

    return (
            <AppShell
                navbar={{
                    width: '260px',
                    breakpoint: 'sm',
                }}
                padding="md"
            >
                <AppShell.Navbar>
                    <Navbar />
                </AppShell.Navbar>

                <AppShell.Main style={{
                    paddingTop: 0,
                    paddingBottom: 0
                }}>
                    <Outlet />
                </AppShell.Main>
            </AppShell>
    )
}

export default Layout