import React, { Component } from "react";

const StatelessCalibrationWidget = ({calibration}) => 
  {
    return(
      <div id="calibration">
          <div id="calibration-status">
            System: {calibration[0]}/3, 
            Gyroscope: {calibration[1]}/3, 
            Accelerometer: {calibration[2]}/3, 
            Magnetometer: {calibration[3]}/3</div>
      </div>
    )
  };

  const CalibrationLevelSetter = ({calibration_level, set_calibration_level}) => 
  {
    return(
      <div id="set_calibration_level">
          <div>
            <input
              type="range"
              id="calibration_level"
              name="Calibration level"
              min="1"
              max="3"
              step="1"
              value={calibration_level}
              onInput={set_calibration_level}  
              list="cal_list"
            />
            <datalist id="cal_list">
              <option value="1" label="Coarse"></option>
              <option value="2" label="Medium"></option>
              <option value="3" label="Fine"></option>
          </datalist>

          </div>
      </div>
    )
  };

export {StatelessCalibrationWidget, CalibrationLevelSetter};
