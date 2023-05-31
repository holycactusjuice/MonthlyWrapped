import React from "react";
import "./styles/styles.css";
import "./styles/home.css";
import ArrowButton from "./components/ArrowButton.js";

const HomePage = ({ totalTracks, totalListens, totalSeconds }) => {
    let seconds = totalSeconds % 60;
    let minutes = Math.floor(Math.floor(seconds / 60) / 60);
    let hours = Math.floor(seconds / 3600);

    return (
        <div className="main-container">
            <div className="greeting">hi there, patpatpatat!</div>
            <div className="main-text-container">
                <div className="minor-text">this month, you've listened to</div>
                <div className="major-text">{totalTracks} tracks</div>
                <div className="minor-text">a combined</div>
                <div className="major-text">{totalListens} times</div>
                <div className="minor-text">for a total of</div>
                <div className="major-text">
                    {hours} hours, {minutes} minutes, {seconds} seconds
                </div>
            </div>
            <div className="bottom-text">
                see how your listening time is split up
            </div>
            <div className="arrow-btn">
                <ArrowButton></ArrowButton>
            </div>
        </div>
    );
};

export default HomePage;
