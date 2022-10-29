// https://codesandbox.io/s/react-leaflet-description-button-o66nb?file=/src/Description.js:0-1349
// https://stackoverflow.com/questions/68414583/custom-button-on-the-leaflet-map-with-react-leaflet-version3
// https://stackoverflow.com/questions/66500181/how-to-locate-react-leaflet-map-to-users-current-position-and-get-the-borders-f

import React, { Component } from "react";
import { useMap } from "react-leaflet";
import L, { LeafletMouseEvent, Map } from "leaflet";

class GeolocateButton extends React.Component {
  helpDiv;

  createButtonControl() {
    const MapHelp = L.Control.extend({
      onAdd: (map) => {
        const helpDiv = L.DomUtil.create("button", "");
        this.helpDiv = helpDiv;
        helpDiv.innerHTML = this.props.title;

        helpDiv.addEventListener("click", () => {
          map.locate().on("locationfound", function (e) {
            console.log("Found it!"+ e.latlng)
            console.log(this.props.locationClickHandler)
            this.props.locationClickHandler(e.latlng.lat, e.latlng.lng);
            // setPosition(e.latlng);
            map.flyTo(e.latlng, map.getZoom());
            const radius = e.accuracy;
            const circle = L.circle(e.latlng, radius);
            circle.addTo(map);
            // setBbox(e.bounds.toBBoxString().split(","));
          });
          
          console.log(map.getCenter());
          // const marker = L.marker()
          //   .setLatLng(this.props.markerPosition)
          //   .bindPopup(this.props.description)
          //   .addTo(map);

          // marker.openPopup();
        });

        //a bit clueless how to add a click event listener to this button and then
        // open a popup div on the map
        return helpDiv;
      }
    });
    return new MapHelp({ position: this.props.buttonposition });
  }

  componentDidMount() {
    const { map } = this.props;
    const control = this.createButtonControl();
    control.addTo(map);
  }

  componentWillUnmount() {
    this.helpDiv.remove();
  }

  render() {
    return null;
  }
}

function withMap(Component) {
  return function WrappedComponent(props) {
    const map = useMap();
    return <Component {...props} map={map} />;
  };
}

export default withMap(GeolocateButton);
