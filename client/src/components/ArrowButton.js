import React from "react";
import arrow from "../images/white-arrow.png";
import axios from "axios";

const ArrowButton = () => {
    const handleClick = () => {
        axios
            .get("/tracks")
            .then((response) => {
                console.log(response.data);
            })
            .catch((error) => {
                console.error(error);
            });
    };

    return (
        <div>
            <button onClick={handleClick} className="arrow-btn">
                <img src={arrow} height="15" alt="arrow" />
            </button>
        </div>
    );
};

export default ArrowButton;
