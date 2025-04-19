import { Route, Routes } from 'react-router-dom'; 
import About from '../pages/Services/About';
import Home from '../pages/home/home'; 
import MainLayout from '../layouts/MainLayout';

const AppRoutes = () => {
    return (
        <Routes>
            <Route element={<MainLayout/>}>
                <Route path="/" element={<Home />} />
                <Route path="/about" element={<About />} />

            </Route>
        </Routes>
    );
};

export default AppRoutes;
