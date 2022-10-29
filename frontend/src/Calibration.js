import React, { Component } from "react";

const StatelessCalibrationWidget = ({calibration}) => 
  {
    return(
      <div id="calibration">
          <h2> Calibration Status </h2>
          <div id="calibration-status">
            System: {calibration[0]}/3, 
            Gyroscope: {calibration[1]}/3, 
            Accelerometer: {calibration[2]}/3, 
            Magnetometer: {calibration[3]}/3</div>
      </div>
    )
  };


export default StatelessCalibrationWidget;
