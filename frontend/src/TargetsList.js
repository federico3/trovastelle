import React, { Component } from "react";

const TargetsList = ({targets_list, reset_targets_list}) => 
{
    let targets_table = targets_list.features.map(
        (target) => <Target target_properties={target}/> 
    );
    return(
        <div id="Targets">
            <table className="styled-table">
                <thead>
                    <tr key="header">
                        <th key="order">#</th>
                        <th key="name">Nome</th>
                        <th key="type">Tipo</th>
                        <th key="start_time">Inizio</th>
                        <th key="end_time">Fine</th>
                        <th key="RA">RA</th>
                        <th key="dec">Dec</th>
                    </tr>
                </thead>
                
                <tbody>
                    {targets_table}
                </tbody>
            </table>
            <form onSubmit={reset_targets_list}>
                <input type="submit" className="btn btn-default" value="Reset"/>
              </form>
        </div>
    );
};

const Target = (target_properties) => 
{
    return(
        <tr key={target_properties.target_properties.properties.order}>
            <th key="order">{target_properties.target_properties.properties.order+1}</th>
            <th key="name">{target_properties.target_properties.properties.name}</th>
            <th key="type">{target_properties.target_properties.properties.type}</th>
            <th key="start_time">{target_properties.target_properties.properties.start_time}</th>
            <th key="end_time">{target_properties.target_properties.properties.end_time}</th>
            <th key="ra">{target_properties.target_properties.geometry.coordinates[0]}</th>
            <th key="dec">{target_properties.target_properties.geometry.coordinates[1]}</th>
         </tr>
    );
};

export {TargetsList, Target};
