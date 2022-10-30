import React, { Component } from "react";

import { MapContainer, TileLayer, useMap, useMapEvents, Marker, Popup } from 'react-leaflet'


function MapManualLocator(props) {
  const map = useMapEvents({
    click: (e) => {
      props.locationClickHandler(e.latlng.lat, e.latlng.lng);
    },
  })
  return null
}

function ObserverMarker(props) {
  const observer = props.observer;
  // const markerRef = useRef(null);
  // const eventHandlers = useMemo(
  //   () => ({
  //     dragend() {
  //       const marker = markerRef.current
  //       // if (marker != null) {
  //         console.log(marker.getLatLng())
  //         props.locationClickHandler(marker.getLatLng().lat, marker.getLatLng().lng);
  //       // }
  //     },
  //   }),
  //   [],
  // )

  const mapRef = useMap();

  if (mapRef) {
        if (!mapRef.getBounds().contains(observer)) {
          // console.log("Marker out of bounds!")
          mapRef.flyTo(observer, mapRef.getZoom())
        } else {
          // console.log("Marker in bounds :)")
        }
    } else {
      // console.log("mapRef is not a thing!");
    }

  return observer === null ? null : (
    <Marker 
      position={observer}
      draggable={false}
      // ref={markerRef}
    >
      <Popup>
        Observer's location:<br /> {observer[0].toFixed(4)} N, {observer[1].toFixed(4)} E.
      </Popup>
    </Marker>
  ) 
}

class ObserverMap extends React.Component{
  constructor(props) {
    super(props);
    this.state = {
      geolocation: "none"
    }
    // this.state = {
    //   observer: {
    //     lat: 33.,
    //     lng: -118.,
    //     alt: 0,
    //   },
    //   hostname: props.hostname,
    //   error: null
    // }
    console.log(this.props.observer);
    this.locationUpdater = props.locationUpdater;
  }

  // componentDidMount() {
  //   fetch("http://"+this.state.hostname+":5000/observer")
  //   .then(res => res.json())
  //   .then(
  //     (result) => {
  //       this.setState({
  //         observer: {
  //           lat: result.lat_deg_N,
  //           lng: result.lon_deg_E,
  //           alt: result.alt_m,
  //         }
  //       });
  //     },
  //     (error) => {
  //       this.setState({
  //         error: error
  //       });
  //     }
  //   );
  // }
  // If the state changed, update the location of the observer!
  componentDidUpdate() {
    // fetch(
    //   "http://"+this.state.hostname+":5000/observer/",
    //   {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json'
    //     },
    //     body: JSON.stringify({"lat_deg_N": this.observer.lat, "lon_deg_E": this.state.observer.lng, "alt_m": this.state.observer.alt})
    //   }
    // )
    // .then(res => res.json())
    // .then(
    //   (result) => {
    //     console.log(result)
    //   },
    //   (error) => {
    //     console.log(error)
    //   }
    // );
    return;
  }
  onMapClick = (lat, lng) => {
    console.log("Clicked on the map! Setting state to lat "+ lat+", long"+lng);
    // this.setState({
    //   observer: {
    //     lat: lat,
    //     lng: lng,
    //     alt: 0.,
    //   },
    // })
    this.props.locationUpdater(
      {
        lat_deg_N: lat,
        lon_deg_E: lng,
        alt_m: 0.,
      }
    )
  }

  geolocate = () => {
    console.log("Invoking location services");
    this.setState({
      geolocation: "waiting"
    });
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(this.geolocationSuccess, this.geolocationError);
    } else {
      console.log("Geolocation is not supported by this browser");
    }  
  };

  geolocationSuccess = (position) => {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    // getMap(latitude, longitude);
    // this.setState({
    //   observer: {
    //     lat: latitude,
    //     lng: longitude,
    //     alt: 0.,
    //   },
    // })
    this.setState({
      geolocation: "found"
    });
    this.props.locationUpdater(
      {
        lat_deg_N: latitude,
        lon_deg_E: longitude,
        alt_m: 0.,
      }
    )
  };
  
  geolocationError = () => {
    this.setState({
      geolocation: "error"
    });
    console.log("Unable to retrieve location");
  };

  geolocationStatusSpan = () => {
    console.log()
    if (this.state.geolocation === "waiting") {return "Waiting"} else
    if (this.state.geolocation === "found")   {return "Found!"} else
    if (this.state.geolocation === "error") {return "⚠️ Error"} else
    {return ""};
  }

  render() {
    const observer = [this.props.observer.lat_deg_N, this.props.observer.lon_deg_E];

    return(
      <div>
        <h2> Observer </h2>
      <div> Click on the map to set the observer's location.
        <button onClick={this.geolocate}>📍 Find my position.</button>
        <span id="geolocationStatus">{this.geolocationStatusSpan()}</span>
      </div>
      <MapContainer 
        center={observer} zoom={10}
        scrollWheelZoom={false}
      >
        <MapManualLocator 
          locationClickHandler={this.onMapClick}
        />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ObserverMarker
          observer={observer}
          locationClickHandler={this.onMapClick}
        />
      </MapContainer>
      </div>
    )
  }
}

export {ObserverMap};
