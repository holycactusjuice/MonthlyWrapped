import React from "react";
import "./styles/styles.css";
import logo from "./images/temp_logo.png";

const BaseLayout = ({ isLoggedIn, children }) => {
    return (
        <div className="container full-height-grow">
            {/* common header */}
            <header className="main-header">
                <a href="/" className="brand-logo">
                    <img src={logo} alt="logo" height="40" />
                    <div className="brand-logo-name">monthlyWrapped</div>
                </a>
                <nav className="main-nav">
                    {isLoggedIn ? (
                        // header elements to display when logged in
                        <ul>
                            <li>
                                <a href="/about">about</a>
                            </li>
                            <li>
                                <a href="/">home</a>
                            </li>
                            <li>
                                <a href="/tracks">tracks</a>
                            </li>
                            <li>
                                <a href="/logout">logout</a>
                            </li>
                        </ul>
                    ) : (
                        // header elements to display when not logged in
                        <ul>
                            <li>
                                <a href="/about">about</a>
                            </li>
                            <li>
                                <a href="/login">login</a>
                            </li>
                        </ul>
                    )}
                </nav>
            </header>
            {/* main content */}
            <main>{children}</main>
        </div>
    );
};

export default BaseLayout;
