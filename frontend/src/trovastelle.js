import React from 'react';


// Bootstrap CSS
import "bootstrap/dist/css/bootstrap.min.css";
// Bootstrap Bundle JS
import "bootstrap/dist/js/bootstrap.bundle.js";

// My CSS
import './trovastelle.css';
// import './freelancer.css';

import MyCelestialMap from './CelestialMap';
import {ObserverMap} from './ObserverMap';
import {StatelessCalibrationWidget, CalibrationLevelSetter} from './Calibration';
import StatelessObservablesWidget from './Observables';
import SimulatedWidget from './Simulated';
import RefreshRateWidget from './RefreshRate';
import ObservablesPropsWidget from './ObservablesProps';
import HardwareWidget from './hardware';
import { TargetsList } from './TargetsList';
import AlertWidget from './AlertState';

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
            list: {"type": "FeatureCollection", "features": []},
            simulated: {"led": true, "ndof": true, "motors": true, "display": true},
            refresh_rate_hz: 1.0,
            calibration_level: 3,
            backend_state: "Waiting",
            backend_message: "",
            error: null,
        }

        if (process.env.NODE_ENV === "production") {
          this.backend_uri = "/api";
        } else {
          this.backend_uri = "http://127.0.0.1:5005";
        }
        // console.log(process.env.NODE_ENV);
        // console.log(this.backend_uri);
        
    }
    
    updateLocation = (new_location) => {
      console.log("updateLocation fired!")
      this.setState(
        {
          observer: new_location
        }
      );
    }

    setConfig = (result) => {
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
        calibration_level: result.calibration_level,
      });
    }
    
    fetchData = (myrequest) => {
      this.setState({
        backend_state: "Waiting",
        backend_message: "Fetching data...",
      });

      let list_fetched = 0;
      let observer_fetched = 0;
      let config_fetched = 0;
      let calibration_fetched = 0;

      let fetch_state = (list_fetched, observer_fetched, config_fetched, calibration_fetched) => {
        let _state = "Processing";
        if (list_fetched === 1 & observer_fetched === 1 & config_fetched === 1 & calibration_fetched === 1){
          _state = "OK";
        } else if (list_fetched === -1 | observer_fetched === -1 | config_fetched === -1 | calibration_fetched === -1) {
          _state = "Error";
        }
        let _msg = "Data: ";
        _msg += (list_fetched === 1? "✔️": (list_fetched === -1? "❌": "⌛")) + " list, ";
        _msg += (observer_fetched === 1? "✔️": (observer_fetched === -1? "❌": "⌛")) + " observer, ";
        _msg += (config_fetched === 1? "✔️": (config_fetched === -1? "❌": "⌛")) + " configuration, ";
        _msg += (calibration_fetched === 1? "✔️": (calibration_fetched === -1? "❌": "⌛")) + " calibration.";
        return [_msg, _state];
      }


      fetch(this.backend_uri+"/list")
      .then(res => res.json())
      .then(
        (result) => {
          list_fetched = 1;
          let [_notification_message, _notification_state] = fetch_state(list_fetched, observer_fetched, config_fetched, calibration_fetched);
          this.setState({
            active: true,
            list: result,
            backend_state: _notification_state,
            backend_message: _notification_message,
          });
          console.log("Fetched list!");
          console.log(this.state.list);
        },
        (error) => {
          list_fetched = -1;
          console.log("Failed to fetch list!");
          console.log(this.state.list);
          let [_notification_message, _notification_state] = fetch_state(list_fetched, observer_fetched, config_fetched, calibration_fetched);
          this.setState({
            active: true,
            backend_state: _notification_state,
            backend_message: _notification_message,
          });
        }
      );

      fetch(this.backend_uri+"/observer")
      .then(res => res.json())
      .then(
        (result) => {
          observer_fetched = 1;
          let [_notification_message, _notification_state] = fetch_state(list_fetched, observer_fetched, config_fetched, calibration_fetched);
          this.setState({
            observer: {
              lat_deg_N: result.lat_deg_N,
              lon_deg_E: result.lon_deg_E,
              alt_m: result.alt_m,
            },
            backend_state: _notification_state,
            backend_message: _notification_message,
          });

        },
        (error) => {
          observer_fetched = -1;
          let [_notification_message, _notification_state] = fetch_state(list_fetched, observer_fetched, config_fetched, calibration_fetched);
          this.setState({
            backend_state: _notification_state,
            backend_message: _notification_message,
          });

        }
      );

      fetch(this.backend_uri+"/config")
      .then(res => res.json())
      .then(
        (result) => {
          config_fetched = 1;
          let [_notification_message, _notification_state] = fetch_state(list_fetched, observer_fetched, config_fetched, calibration_fetched);
          this.setConfig(result);
          this.setState({
            backend_state: _notification_state,
            backend_message: _notification_message,
          });
        },
        (error) => {
          config_fetched = -1;
          let [_notification_message, _notification_state] = fetch_state(list_fetched, observer_fetched, config_fetched, calibration_fetched);
          this.setState({
            active: true,
            backend_state: _notification_state,
            backend_message: _notification_message,
          });

        }
      );
      fetch(this.backend_uri+"/calibration")
      .then(res => res.json())
      .then(
        (result) => {
          calibration_fetched = 1;
          let [_notification_message, _notification_state] = fetch_state(list_fetched, observer_fetched, config_fetched, calibration_fetched);
          this.setState({
            active: true,
            calibration: result,
            backend_state: _notification_state,
            backend_message: _notification_message,
          });

        },
        (error) => {
          calibration_fetched = -1;
          let [_notification_message, _notification_state] = fetch_state(list_fetched, observer_fetched, config_fetched, calibration_fetched);
          this.setState({
            active: true,
            backend_state: _notification_state,
            backend_message: _notification_message,
          });
        }
      );

      if (typeof myrequest !== 'undefined'){
        myrequest.preventDefault();
      }
    }

    pushConfig = (myrequest) => {
      this.setState({
        backend_state: "Waiting",
        backend_message: "Pushing new configuration...",
      });

      fetch(
        this.backend_uri+"/config/",
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
          this.setConfig(result);
          this.setState({
            backend_state: "OK",
            backend_message: "New configuration pushed!",
          });
          this.fetchData();
        },
        (error) => {
          console.log(error);
          this.setState({
            backend_state: "Error",
            backend_message: "Error pushing new configuration!",
          });
          this.fetchData();
        }
      );
      if (typeof myrequest !== 'undefined'){
        myrequest.preventDefault();
      }
      
    }

    resetList = (myrequest) => {
      this.setState({
        backend_state: "Waiting",
        backend_message: "Updating observables list...",
      });
      fetch(
        this.backend_uri+"/list/",
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          },
          body: "",
        }
      )
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            active: true,
            list: result
          });
          this.setState({
            backend_state: "OK",
            backend_message: "Loaded new list!",
          });
        },
        (error) => {
          console.log(error);
          this.setState({
            backend_state: "Error",
            backend_message: "Error updating observables list!",
          });
        }
      );
      if (typeof myrequest !== 'undefined'){
        myrequest.preventDefault();
      }
      // this.fetchData();
    }

    componentDidMount() {
      this.fetchData();
    }

    componentDidUpdate(){
      // If the state updated, send a POST request to the server
      // Examine the output
      // If the output has changed
      // Update the state (which will trigger another componentDidUpdate!)
      // this.pushConfig();
    }

    render() {
        return (
        <div> 
          <nav className="navbar navbar-fixed-top navbar-light bg-light">
            <div className="container">
              <span className="navbar-brand mb-0 h1">Trovastelle!</span>
              <form onSubmit={this.fetchData}>
                <input type="submit" className="btn btn-info navbar-btn" value="Fetch"/>
              </form>
              <form onSubmit={this.pushConfig}>
                <input type="submit" className="btn btn-primary navbar-btn" value="Upload"/>
              </form>
            </div>
          </nav>
          {/* <nav id="mainNav" className="navbar navbar-default navbar-fixed-top navbar-custom">
            <div class="navbar-header page-scroll">
              <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
                  <span class="sr-only">Toggle navigation</span>
                  <span class="icon-bar"></span>
                  <span class="icon-bar"></span>
                  <span class="icon-bar"></span>
              </button>
              <h1>Trovastelle!</h1>
            </div>
            <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                <ul class="nav navbar-nav navbar-right">
                    <li class="page-scroll">
                        <a href="#page-top">About</a>
                    </li>
                    <li class="page-scroll">
                        <a href="#research">Research</a>
                    </li>
                </ul>
            </div>
          </nav> */}
          <AlertWidget 
           status={this.state.backend_state}
           message={this.state.backend_message}
           error={this.state.error}
          />
          <div className='skymap'>
            <h2> Sky Map </h2>
            <MyCelestialMap
              backend_uri={this.backend_uri}
              observer={this.state.observer}
              list={this.state.list}
              visibility_window={this.state.observables_list["visibility_window"]}
              show_visibility_window={this.state.observables_list["check_visible"]}
            />
          </div>
          <div className='targetlist'>
            <h2> Targets </h2>
            <TargetsList
              targets_list={this.state.list}
              reset_targets_list={this.resetList}
              />
          </div>
          <div>
            <h2>Observables</h2>
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
            <h2>Observable properties</h2>
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
          <div>
            <h2> Observer </h2>
            <ObserverMap 
              observer={this.state.observer}
              locationUpdater={this.updateLocation}
            />
          </div>
          <div>
            <h2> Calibration </h2>
            <h3> Status </h3>
            <StatelessCalibrationWidget 
              calibration={this.state.calibration}
            />
            <h3>Level</h3>
            <CalibrationLevelSetter
              calibration_level={this.state.calibration_level}
              set_calibration_level={(r)=> {this.setState({calibration_level: parseInt(r.target.value)}); return 0;}}
            />
          </div>
          <details>
            <summary>
              Advanced settings
            </summary>
            <div>
              <h3>Simulation</h3>
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
              <h3>Hardware refresh rate</h3>
              <RefreshRateWidget
                refreshRate={this.state.refresh_rate_hz}
                updateRefreshRate={ (r)=>{this.setState({refresh_rate_hz: parseFloat(r.target.value)});}}
              />
            </div>
            <div>
            <h3>Stepper motors and LEDs</h3>
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
