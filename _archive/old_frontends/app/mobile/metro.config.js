const { getDefaultConfig } = require("expo/metro-config");
const path = require("path");

const config = getDefaultConfig(__dirname);

const WEB_STUBS = {
  "react-native-maps": path.resolve(__dirname, "stubs/react-native-maps.js"),
  "react-native-screens": path.resolve(__dirname, "stubs/react-native-screens.js"),
};

config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (platform === "web" && WEB_STUBS[moduleName]) {
    return {
      filePath: WEB_STUBS[moduleName],
      type: "sourceFile",
    };
  }
  return context.resolveRequest(context, moduleName, platform);
};

module.exports = config;
