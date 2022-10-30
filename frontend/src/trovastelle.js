import './trovastelle.css';
import React, { Component, useRef, useMemo } from 'react';

import MyCelestialMap from './CelestialMap';
import {ObserverMap} from './ObserverMap';
import {StatelessCalibrationWidget, CalibrationLevelSetter} from './Calibration';
import StatelessObservablesWidget from './Observables';
import SimulatedWidget from './Simulated';
import RefreshRateWidget from './RefreshRate';
import ObservablesPropsWidget from './ObservablesProps';
import HardwareWidget from './hardware';
import { TargetsList } from './TargetsList';

class Trovastelle extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            active: true,
            calibration: [0,2,0,0],
            // configuration: { , },
            observables: {"satellites": true, "missions": true, "planets": true, "smallbodies": true, "mellyn": false, "messiers": false},
            observer: {"lat_deg_N": 33, "lon_deg_E": -118, "alt_m": 204},
            led_pins: {"red": 5, "green": 6, "blue": 13, "alpha": 19, "anode_high": false, "voltage_scale": 1.0},
            led_color_scheme: "strong",
            steppers: {"steps_per_turn_alt": 2052, "steps_per_turn_az": 533, "alt_direction_up": 2, "az_direction_cw": 2},
            observables_list: {
              "time_on_target_s": 150,
              "target_list_length_s": 600,
              "check_visible": true,
              "visibility_window": {
                "min_alt_rad": -1.57,
                "max_alt_rad": 1.57,
                "min_az_rad": 0.0,
                "max_az_rad": 6.28
              },
            },
            list: {"features": []},
            simulated: {"led": true, "ndof": true, "motors": true, "display": true},
            refresh_rate_hz: 1.0,
            calibration_level: 3,
            error: null,
        }

        this.backend_uri = "127.0.0.1:5005"
    }
    
    updateLocation = (new_location) => {
      console.log("updateLocation fired!")
      this.setState(
        {
          observer: new_location
        }
      );
    }
    
    componentDidMount() {
        fetch("http://"+this.backend_uri+"/list")
        .then(res => res.json())
        .then(
          (result) => {
            this.setState({
              active: true,
              list: result
            });
          },
          (error) => {
            this.setState({
              active: true,
              error: error
            });
          }
        );
        fetch("http://"+this.backend_uri+"/observer")
        .then(res => res.json())
        .then(
          (result) => {
            this.setState({
              observer: {
                lat_deg_N: result.lat_deg_N,
                lon_deg_E: result.lon_deg_E,
                alt_m: result.alt_m,
              }
            });
          },
          (error) => {
            this.setState({
              error: error
            });
          }
        );

        fetch("http://"+this.backend_uri+"/config")
        .then(res => res.json())
        .then(
          (result) => {
            this.setState({
              active: true,
              configuration: result,
              observables: result.observables,
              led_pins: result.led_pins,
              led_color_scheme: result.led_color_scheme,
              steppers: result.steppers,
              observables_list: result.observables_list,
              simulated: result.simulated,
              refresh_rate_hz: result.refresh_rate_hz,
            });
          },
          (error) => {
            this.setState({
              active: true,
              error: error
            });
          }
        );
        fetch("http://"+this.backend_uri+"/calibration")
        .then(res => res.json())
        .then(
          (result) => {
            this.setState({
              active: true,
              calibration: result
            });
          },
          (error) => {
            this.setState({
              active: true,
              error: error
            });
          }
        );
    }

    componentDidUpdate(){
      // If the state updated, send a POST request to the server
      // Examine the output
      // If the output has changed
      // Update the state (which will trigger another componentDidUpdate!)
      fetch(
        "http://"+this.backend_uri+"/config/",
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(
            this.state,
          //   {"lat_deg_N": this.state.observer.lat, "lon_deg_E": this.state.observer.lng, "alt_m": this.state.observer.alt}
            )
        }
      )
      .then(res => res.json())
      .then(
        (result) => {
          console.log(result)
        },
        (error) => {
          console.log(error)
        }
      );
    }

    render() {
        return (
        <div> <h1>Trovastelle!</h1> 
          <div>

          </div>
          <div>
            <MyCelestialMap
              backend_uri={this.backend_uri}
              observer={this.state.observer}
              list={this.state.list}
            />
          </div>
          <div>
            <TargetsList targets_list={this.state.list}/>
          </div>
          <div>
            <ObserverMap 
              observer={this.state.observer}
              locationUpdater={this.updateLocation}
            />
          </div>

          <div>
            <StatelessCalibrationWidget 
              calibration={this.state.calibration}
            />
            <CalibrationLevelSetter
              calibration_level={this.state.calibration_level}
              set_calibration_level={(r)=> {this.setState({calibration_level: r.target.value}); return 0;}}
            />
          </div>
          <div>
            <StatelessObservablesWidget 
              observables={this.state.observables}
              checkObservables={ {
                "satellites":   ()=>{var oState = this.state.observables; oState.satellites =   !oState.satellites;   this.setState({observables: oState}); return 0},
                "missions":     ()=>{var oState = this.state.observables; oState.missions =     !oState.missions;     this.setState({observables: oState}); return 0},
                "planets":      ()=>{var oState = this.state.observables; oState.planets =      !oState.planets;      this.setState({observables: oState}); return 0},
                "smallbodies":  ()=>{var oState = this.state.observables; oState.smallbodies =  !oState.smallbodies;  this.setState({observables: oState}); return 0},
                "messiers":     ()=>{var oState = this.state.observables; oState.messiers =     !oState.messiers;     this.setState({observables: oState}); return 0},
                "mellyn":       ()=>{var oState = this.state.observables; oState.mellyn =       !oState.mellyn;       this.setState({observables: oState}); return 0},
                }
              }
            />
          </div>
          <div>
            <ObservablesPropsWidget
              observablesProps= {this.state.observables_list}
              updateObservablesProps=
              {
                {
                  "time_on_target_s": (r)=>{var olState = this.state.observables_list; olState.time_on_target_s =   parseInt(r.target.value);   this.setState({observables_list: olState}); return 0},
                  "target_list_length_s": (r)=>{var olState = this.state.observables_list; olState.target_list_length_s =   parseInt(r.target.value);   this.setState({observables_list: olState}); return 0},
                  "check_visible": (r)=>{var olState = this.state.observables_list; olState.check_visible =   !olState.check_visible;   this.setState({observables_list: olState}); return 0},
                  "visibility_window": {
                    "min_alt_rad": (r)=>{var olState = this.state.observables_list; olState.visibility_window.min_alt_rad =  parseFloat(r.target.value)*Math.PI/180.;   this.setState({observables_list: olState}); return 0},
                    "max_alt_rad": (r)=>{var olState = this.state.observables_list; olState.visibility_window.max_alt_rad =  parseFloat(r.target.value)*Math.PI/180.;   this.setState({observables_list: olState}); return 0},
                    "min_az_rad":  (r)=>{var olState = this.state.observables_list; olState.visibility_window.min_az_rad =   parseFloat(r.target.value)*Math.PI/180.;   this.setState({observables_list: olState}); return 0},
                    "max_az_rad":  (r)=>{var olState = this.state.observables_list; olState.visibility_window.max_az_rad =   parseFloat(r.target.value)*Math.PI/180.;   this.setState({observables_list: olState}); return 0},
                  }
                }
              }
            />
          </div>
          <details>
            <summary>
              <h2>Advanced settings</h2>
            </summary>
            <div>
              <SimulatedWidget 
                simulated={this.state.simulated}
                checkSimulated={ {
                  "led":      ()=>{var sState = this.state.simulated; sState.led      =  !sState.led;     this.setState({simulated: sState}); return 0},
                  "9dof":     ()=>{var sState = this.state.simulated; sState["9dof"]  =  !sState["9dof"]; this.setState({simulated: sState}); return 0},
                  "motors":   ()=>{var sState = this.state.simulated; sState.motors   =  !sState.motors;  this.setState({simulated: sState}); return 0},
                  "display":  ()=>{var sState = this.state.simulated; sState.display  =  !sState.display; this.setState({simulated: sState}); return 0},
                  }
                }
              />
              {/* {Object.entries(this.state.simulated).map( ([key, value])=> `${key}: ${value} `)} */}
            </div>
            <div>
              <RefreshRateWidget
                refreshRate={this.state.refresh_rate_hz}
                updateRefreshRate={ (r)=>{this.setState({refresh_rate_hz: parseFloat(r.target.value)});}}
              />
            </div>
            <div>
              <HardwareWidget
                hardwareSettings={{
                  steppers: this.state.steppers,
                  led_color_scheme: this.state.led_color_scheme,
                  led_pins: this.state.led_pins,
                }}
                updateHardwareSettings={{
                  steppers: {
                    steps_per_turn_alt: ((r)=> {var olState = this.state.steppers; olState.steps_per_turn_alt =   parseInt(r.target.value);   this.setState({steppers: olState}); return 0}),
                    steps_per_turn_az: ((r)=> {var olState = this.state.steppers; olState.steps_per_turn_az =   parseInt(r.target.value);   this.setState({steppers: olState}); return 0}),
                    alt_direction_up: ()=>{var sState = this.state.steppers; sState.alt_direction_up === 1 ? sState.alt_direction_up=2 : sState.alt_direction_up=1;     this.setState({steppers: sState}); return 0},
                    az_direction_cw: ()=>{var sState = this.state.steppers; sState.az_direction_cw === 1 ? sState.az_direction_cw=2 : sState.az_direction_cw=1;     this.setState({steppers: sState}); return 0},
                  },
                  led_color_scheme: ()=>{var newColorScheme="strong"; this.state.led_color_scheme === "strong"? newColorScheme="pale": newColorScheme="strong"; this.setState({led_color_scheme: newColorScheme}); return 0;},
                  led_pins: {
                    alpha: ((r)=> {var olState = this.state.led_pins; olState.alpha =   parseInt(r.target.value);   this.setState({led_pins: olState}); return 0}),
                    red: ((r)=> {var olState = this.state.led_pins; olState.red =   parseInt(r.target.value);   this.setState({led_pins: olState}); return 0}),
                    green: ((r)=> {var olState = this.state.led_pins; olState.green =   parseInt(r.target.value);   this.setState({led_pins: olState}); return 0}),
                    blue: ((r)=> {var olState = this.state.led_pins; olState.blue =   parseInt(r.target.value);   this.setState({led_pins: olState}); return 0}),
                    anode_high:()=> {var sState = this.state.led_pins; sState.anode_high=!sState.anode_high; this.setState({steppers: sState}); return 0},
                    voltage_scale: ((r)=> {var olState = this.state.led_pins; olState.voltage_scale =   parseFloat(r.target.value);   this.setState({led_pins: olState}); return 0}),
                  }
                }}
              />
            </div>
          </details>
        </div>
        );
    }
}
  

export default Trovastelle;
