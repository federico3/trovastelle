import React, { Component } from "react";

const ObservablesPropsWidget = ({observablesProps, updateObservablesProps}) => 
{
    return(
        <div id="observablesProps">
            <h2> Observables Properties </h2>
            {/* {Object.entries(observables).map( ([key, value])=> `${key}: ${value} `)} */}
            <div>
                <label htmlFor="time_on_target_s">Time on target [s]:</label>
                <input type="number" step="1" label="time_on_target_s" value={observablesProps.time_on_target_s} onInput={updateObservablesProps.time_on_target_s}/>
            </div>
            <div>
                <label htmlFor="target_list_length_s">Target list duration [s]:</label>
                <input type="number" step="1" label="target_list_length_s" value={observablesProps.target_list_length_s} onInput={updateObservablesProps.target_list_length_s}/>
            </div>
            <div>
                <label htmlFor="check_visible"> Check target visibility</label>
                <input type="checkbox" id="check_visible" checked={observablesProps.check_visible} onChange={updateObservablesProps.check_visible} name="check_visible" value="Check target visibility"/>
            </div>
            <div>
                <div>
                    <label htmlFor="visibility_window_min_alt_deg">Minimum altitude [degrees]:</label>
                    <input type="number" step="1"  min="-90" max="90" label="visibility_window_min_alt_deg" value={observablesProps.visibility_window.min_alt_rad/Math.PI*180.} onInput={updateObservablesProps.visibility_window.min_alt_rad}/>
                </div>
                <div>
                    <label htmlFor="visibility_window_max_alt_deg">Maximum altitude [degrees]:</label>
                    <input type="number" step="1" min="-90" max="90" label="visibility_window_max_alt_deg" value={observablesProps.visibility_window.max_alt_rad/Math.PI*180.} onInput={updateObservablesProps.visibility_window.max_alt_rad}/>
                </div>
                <div>
                    <label htmlFor="visibility_window_min_az_deg">Minimum azimuth [degrees]:</label>
                    <input type="number" step="1" min="0" max="360" label="visibility_window_min_az_deg" value={observablesProps.visibility_window.min_az_rad/Math.PI*180.} onInput={updateObservablesProps.visibility_window.min_az_rad}/>
                </div>
                <div>
                    <label htmlFor="visibility_window_max_az_deg">Maximum azimuth [degrees]:</label>
                    <input type="number" step="1" min="0" max="360" label="visibility_window_max_az_deg" value={observablesProps.visibility_window.max_az_rad/Math.PI*180.} onInput={updateObservablesProps.visibility_window.max_az_rad}/>
                </div>
            </div>
        </div>
    );
};

export default ObservablesPropsWidget;
