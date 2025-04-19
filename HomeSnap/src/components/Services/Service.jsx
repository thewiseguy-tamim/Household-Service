import axios from 'axios';
import React, { useEffect, useState } from 'react';
import ServiceItem from './ServiceItem';

const Service = () => {
    const [services, setServices] = useState([]);

    useEffect(() => {
        axios.get("http://127.0.0.1:8000/services")
            .then(res => {
                console.log(res.data.results);
                setServices(res.data.results);
            });
    }, []);

    return (
        <div>
            {services.map(service => (
                <ServiceItem key={service.id} service={service} />
            ))}
        </div>
    );
};

export default Service;
