import React, { Component } from "react";

const AlertWidget = ({status, message, error}) => 
{
    let alert_type = "alert-primary";
    if (status === "OK") {
        alert_type = "alert-success"
    } else if (status === "Waiting") {
        alert_type = "alert-warning"
    } else if (status === "Processing") {
        alert_type = "alert-primary"
    } else if (status === "Error") {
        alert_type = "alert-danger"
    }

    return(
          <div className={"alert top-alert "+alert_type+" alert-dismissible fade show"} role="alert">
            {/* <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button> */}
            {message}
            {error}
          </div>
    );
};

export default AlertWidget;
