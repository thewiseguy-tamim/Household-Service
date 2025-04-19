import React from 'react';
import { Outlet } from 'react-router';
import NavBar from './NavBar';
import Footer from './Footer';

const MainLayout = () => {
    return (
        <>
            <NavBar />
            <Outlet/>
            <Footer/>
        </>
    );
};

export default MainLayout;