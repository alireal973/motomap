const React = require("react");
const { View } = require("react-native");

const MapView = (props) => React.createElement(View, { style: props.style });
MapView.Animated = MapView;

const Polyline = () => null;
const Circle = () => null;
const Marker = () => null;
const Callout = () => null;
const Overlay = () => null;

const PROVIDER_GOOGLE = "google";
const PROVIDER_DEFAULT = null;

module.exports = MapView;
module.exports.default = MapView;
module.exports.Polyline = Polyline;
module.exports.Circle = Circle;
module.exports.Marker = Marker;
module.exports.Callout = Callout;
module.exports.Overlay = Overlay;
module.exports.PROVIDER_GOOGLE = PROVIDER_GOOGLE;
module.exports.PROVIDER_DEFAULT = PROVIDER_DEFAULT;
