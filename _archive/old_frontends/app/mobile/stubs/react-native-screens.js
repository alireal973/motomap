const React = require("react");
const { View } = require("react-native");

const Screen = (props) => React.createElement(View, props);
const ScreenContainer = (props) => React.createElement(View, props);
const ScreenStack = (props) => React.createElement(View, props);
const ScreenStackItem = (props) => React.createElement(View, props);
const FullWindowOverlay = (props) => React.createElement(View, props);

function enableScreens() {}
function enableFreeze() {}
function screensEnabled() { return false; }
function freezeEnabled() { return false; }
function isSearchBarAvailableForCurrentPlatform() { return false; }
function executeNativeBackPress() {}

module.exports = {
  Screen,
  ScreenContainer,
  ScreenStack,
  ScreenStackItem,
  FullWindowOverlay,
  enableScreens,
  enableFreeze,
  screensEnabled,
  freezeEnabled,
  isSearchBarAvailableForCurrentPlatform,
  executeNativeBackPress,
  default: Screen,
};
