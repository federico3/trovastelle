import React, { Component } from "react";

const HardwareWidget = ({hardwareSettings, updateHardwareSettings}) => 
{
    return(
        <div id="hardware">
            <h4> Stepper Motors </h4>
                {/* {Object.entries(simulated).map( ([key, value])=> `${key}: ${value} `)} */}
                <div>
                    <label htmlFor="stepper_steps_per_turn_alt">Steps per turn (alt):</label>
                    <input type="number" step="1" label="stepper_steps_per_turn_alt" value={hardwareSettings.steppers.steps_per_turn_alt} onInput={updateHardwareSettings.steppers.steps_per_turn_alt}/>
                </div>

                <div>
                    <label htmlFor="stepper_steps_per_turn_az">Steps per turn (az):</label>
                    <input type="number" step="1" label="stepper_steps_per_turn_az" value={hardwareSettings.steppers.steps_per_turn_az} onInput={updateHardwareSettings.steppers.steps_per_turn_az}/>
                </div>
                
                <div>
                <input type="checkbox" id="stepper_alt_direction_up" checked={hardwareSettings.steppers.alt_direction_up === 1} onChange={updateHardwareSettings.steppers.alt_direction_up} name="stepper_alt_direction_up" value="stepper_alt_direction_up"/>
                    <label htmlFor="stepper_alt_direction_up"> Altitude stepper forward motion drives the arrow up</label>
                </div>
                <div>
                    <input type="checkbox" id="stepper_az_direction_cw" checked={hardwareSettings.steppers.az_direction_cw === 1} onChange={updateHardwareSettings.steppers.az_direction_cw} name="stepper_az_direction_cw" value="stepper_az_direction_cw"/>
                    <label htmlFor="stepper_az_direction_cw"> Azimuth stepper forward motion drives the arrow clockwise</label>
                </div>

                <h4> LEDs </h4>
                <div>
                    <input type="checkbox" id="led_color_scheme" checked={hardwareSettings.led_color_scheme === "strong"} onChange={updateHardwareSettings.led_color_scheme} name="led_color_scheme_strong" value="led_color_scheme_strong"/>
                    <label htmlFor="led_color_scheme"> Vibrant LED colors on power LED </label>
                </div>
                <h5> LED pins </h5>
                <div>
                    <label htmlFor="led_pin_alpha">Alpha</label>
                    <input type="number" step="1" label="led_pin_alpha" value={hardwareSettings.led_pins.alpha} onInput={updateHardwareSettings.led_pins.alpha}/>
                </div>
                <div>
                    <label htmlFor="led_pin_red">Red</label>
                    <input type="number" step="1" label="led_pin_red" value={hardwareSettings.led_pins.red} onInput={updateHardwareSettings.led_pins.red}/>
                </div>
                <div>
                    <label htmlFor="led_pin_green">Green</label>
                    <input type="number" step="1" label="led_pin_green" value={hardwareSettings.led_pins.green} onInput={updateHardwareSettings.led_pins.green}/>
                </div>
                <div>
                    <label htmlFor="led_pin_blue">Blue</label>
                    <input type="number" step="1" label="led_pin_blue" value={hardwareSettings.led_pins.blue} onInput={updateHardwareSettings.led_pins.blue}/>
                </div>
                <div>
                    <input type="checkbox" id="led_anode_high" checked={hardwareSettings.led_pins.anode_high} onChange={updateHardwareSettings.led_pins.anode_high} name="led_anode_high" value="led_anode_high"/>
                    <label htmlFor="led_anode_high"> LEDs anode is held high </label>
                </div>
                <div>
                    <label htmlFor="led_voltage_scale">LED voltage scale factor</label>
                    <input type="number" step="1" label="led_voltage_scale" value={hardwareSettings.led_pins.voltage_scale} onInput={updateHardwareSettings.led_pins.voltage_scale}/>
                </div>
        </div>
    );
};

export default HardwareWidget;
