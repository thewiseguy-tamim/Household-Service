import axios from 'axios';
import React, { useEffect } from 'react';


const Service = () => {
    useEffect(() => {
        axios.get("https://household-service.vercel.app/services")
            .then(res => console.log(res.data))
    }, []);
    return (
        <div>
            
        </div>
    );
};

export default Service;