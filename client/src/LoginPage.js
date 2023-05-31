import React from "react";
import "./styles/login.css";
import LoginButton from "./components/LoginButton";

const LoginPage = () => {
    return (
        <div>
            <div className="main-container">
                <div className="title">
                    all your listens this month.
                    <br />
                    all in one place.
                </div>
                <LoginButton></LoginButton>
            </div>
            <div className="login-page-circle-1"></div>
            <div className="login-page-circle-2"></div>
            <div className="login-page-circle-3"></div>
            <div className="login-page-circle-4"></div>
        </div>
    );
};

export default LoginPage;
