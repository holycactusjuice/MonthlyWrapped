import React from "react";
import "../styles/login.css";
import axios from "axios";

const LoginButton = () => {
    const handleClick = () => {
        axios
            .get("/spotify-login")
            .then((response) => {
                console.log(response.data);
            })
            .catch((error) => {
                console.error(error);
            });
    };

    return (
        <div>
            <button onClick={handleClick} className="login-btn">
                start tracking
            </button>
        </div>
    );
};

export default LoginButton;
