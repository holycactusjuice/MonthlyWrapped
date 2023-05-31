import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import BaseLayout from "./BaseLayout";
import LoginPage from "./LoginPage";
import HomePage from "./HomePage";
import AboutPage from "./AboutPage";
import TracksPage from "./TracksPage";

const App = () => {
    // default is not logged in
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    return (
        // <BaseLayout
        //     isLoggedIn={isLoggedIn}
        //     children=<LoginPage></LoginPage>
        // ></BaseLayout>
        <Router>
            <Routes>
                <Route element={<BaseLayout />}>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/login" element={LoginPage} />
                    <Route path="/about" element={AboutPage} />
                    <Route path="/tracks" element={TracksPage} />
                </Route>
            </Routes>
        </Router>
    );
};

export default App;
