import React, { Component } from "react";

const RefreshRateWidget = ({refreshRate, updateRefreshRate}) => 
{
    return(
        <div id="refreshRate">
            <h2> Refresh Rate </h2>
            {/* {Object.entries(observables).map( ([key, value])=> `${key}: ${value} `)} */}
            <label htmlFor="refresh-rate">Refresh rate [Hz]:</label>
            <input type="number" step="0.01" label="refresh-rate" value={refreshRate} onInput={updateRefreshRate}/>
        </div>
    );
};

export default RefreshRateWidget;
