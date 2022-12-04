import React, { Component } from "react";

const SimulatedWidget = ({simulated, checkSimulated}) => 
{
    return(
        <div id="simulated">
                {/* {Object.entries(simulated).map( ([key, value])=> `${key}: ${value} `)} */}
                <div>
                <input type="checkbox" id="simulated-led" checked={simulated.led} onChange={checkSimulated.led} name="simulated-led" value="LED"/>
                    <label htmlFor="simulated-led">💡  LED</label>
                </div>
                <div>
                <input type="checkbox" id="simulated-9dof" checked={simulated["9dof"]} onChange={checkSimulated["9dof"]} name="simulated-9dof" value="9DOF Acc/Gyr/Mag"/>
                    <label htmlFor="simulated-9dof">🧭  9DOF Acc/Gyr/Mag</label>
                </div>
                <div>
                <input type="checkbox" id="simulated-motors" checked={simulated.motors} onChange={checkSimulated.motors} name="simulated-motors" value="Motors"/>
                    <label htmlFor="simulated-motors">⚙️ Motors</label>
                </div>
                <div>
                <input type="checkbox" id="simulated-display" checked={simulated.display} onChange={checkSimulated.display} name="simulated-display" value="Display"/>
                    <label htmlFor="simulated-display">📺 Display</label>
                </div>
        </div>
    );
};

export default SimulatedWidget;
