import React, { Component } from "react";

// class ObservablesWidget extends React.Component {
//   constructor(props) {
//       super(props);
//       this.observables = props.observables;
//       this.checkObservables = props.checkObservables
//   }

//   render() {
//       return(
//           <div id="observables">
//               <h2> Observables </h2>
//               {Object.entries(this.observables).map( ([key, value])=> `${key}: ${value} `)}
//                 <input type="checkbox" id="observables-satellites" checked={this.observables.satellites} onChange={this.checkObservables.satellites} name="observables-satellites" value="Satellites"/>
//                     <label htmlFor="observables-satellites"> 🛰️ Satellites</label>
//                 <input type="checkbox" id="observables-missions" checked={this.observables.missions} onChange={this.checkObservables.missions} name="observables-missions" value="Missions"/>
//                     <label htmlFor="observables-missions"> 🚀 Missions</label>
//                 <input type="checkbox" id="observables-planets" checked={this.observables.planets} onChange={this.checkObservables.planets} name="observables-planets" value="planets"/>
//                     <label htmlFor="observables-planets"> 🪐 Planets</label>
//                 <input type="checkbox" id="observables-smallbodies" checked={this.observables.smallbodies} onChange={this.checkObservables.smallbodies} name="observables-smallbodies" value="smallbodies"/>
//                     <label htmlFor="observables-smallbodies"> ☄️ Small bodies</label>
//                 <input type="checkbox" id="observables-messiers" checked={this.observables.messiers} onChange={this.checkObservables.messiers} name="observables-messiers" value="messiers"/>
//                     <label htmlFor="observables-messiers"> 🌌 Messiers</label>
//                 <input type="checkbox" id="observables-mellyn" checked={this.observables.mellyn} onChange={this.checkObservables.mellyn} name="observables-mellyn" value="mellyn"/>
//                     <label htmlFor="observables-mellyn"> 🧑 Mellyn</label>
//           </div>
//       );
//   }
// }

const StatelessObservablesWidget = ({observables, checkObservables}) => 
{
    return(
        <div id="observables">
            {/* {Object.entries(observables).map( ([key, value])=> `${key}: ${value} `)} */}
            <div>
              <input type="checkbox" id="observables-satellites" checked={observables.satellites} onChange={checkObservables.satellites} name="observables-satellites" value="Satellites"/>
                  <label htmlFor="observables-satellites"> 🛰️ Satellites</label>
            </div>
            <div>
              <input type="checkbox" id="observables-missions" checked={observables.missions} onChange={checkObservables.missions} name="observables-missions" value="Missions"/>
                  <label htmlFor="observables-missions"> 🚀 Missions</label>
            </div>
            <div>
              <input type="checkbox" id="observables-planets" checked={observables.planets} onChange={checkObservables.planets} name="observables-planets" value="planets"/>
                  <label htmlFor="observables-planets"> 🪐 Planets</label>
            </div>
            <div>
              <input type="checkbox" id="observables-smallbodies" checked={observables.smallbodies} onChange={checkObservables.smallbodies} name="observables-smallbodies" value="smallbodies"/>
                  <label htmlFor="observables-smallbodies"> ☄️ Small bodies</label>
            </div>
            <div>
              <input type="checkbox" id="observables-messiers" checked={observables.messiers} onChange={checkObservables.messiers} name="observables-messiers" value="messiers"/>
                  <label htmlFor="observables-messiers"> 🌌 Messiers</label>
            </div>
            <div>
              <input type="checkbox" id="observables-mellyn" checked={observables.mellyn} onChange={checkObservables.mellyn} name="observables-mellyn" value="mellyn"/>
                  <label htmlFor="observables-mellyn"> 🧑 Mellyn</label>
            </div>
        </div>
    );
};



export default StatelessObservablesWidget;
