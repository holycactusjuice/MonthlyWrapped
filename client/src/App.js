import React, { useState, useEffect } from "react";
import axios from "axios";

const HomePage = () => {
    const [sortOption, setSortOption] = useState("listenCount"); // default sorting option is listen count
    const [listenData, setListenData] = useState([]);

    const handleSortOptionChange = (option) => {
        setSortOption(option);
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get("/api/listen-data");
                setListenData(response.data);
            } catch (error) {
                console.log("Error fetching listen data:", error);
            }
        };
        fetchData();
    }, []);

    return (
        <div>
            <div>Album Art</div>
            <div>Title</div>
            <div>Listen Count</div>
            <div>Time Listened (s)</div>
            {listenData.map((track) => (
                <div key={track.id}>
                    <div>{track.album_art_url}</div>
                    <div>{track.title}</div>
                    <div>{track.listen_count}</div>
                    <div>{track.time_listened}</div>
                </div>
            ))}
        </div>
    );
};

export default HomePage;
