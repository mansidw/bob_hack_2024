// App.js
import React, { useContext } from "react";
import { StyleSheet, View } from "react-native";
import { createStackNavigator } from "@react-navigation/stack";
import { NavigationContainer } from "@react-navigation/native";
import { LogBox } from "react-native";
import registerNNPushToken from "native-notify";
import Register from "./screens/Register";
import Login from "./screens/Login";
import Home from "./screens/Home";
import Chatbot from "./screens/Chatbot";
import { UserProvider, UserContext } from "./UserContext";
import TopNavbar from "./components/TopNavbar";
import { SafeAreaProvider } from "react-native-safe-area-context";

const Stack = createStackNavigator();

const AppStack = () => {
  const { user } = useContext(UserContext);

  return (
    <View style={{ flex: 1 }}>
      {/* Render TopNavbar only if user is logged in */}
      {user && <TopNavbar />}
      <Stack.Navigator>
        {user ? (
          <>
            <Stack.Screen name="Home" component={Home} />
            <Stack.Screen name="BOBBhandu" component={Chatbot} />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={Login} />
            <Stack.Screen name="Register" component={Register} />
          </>
        )}
      </Stack.Navigator>
    </View>
  );
};

export default function App() {
  registerNNPushToken(22691, "GNcqpcDMoJaUg3CZA7HF9Q");
  LogBox.ignoreLogs(["Warning: ..."]); // Ignore log notification by message
  LogBox.ignoreAllLogs(); // Ignore all log notifications

  return (
    <UserProvider>
      <SafeAreaProvider>
        <NavigationContainer>
          <AppStack />
        </NavigationContainer>
      </SafeAreaProvider>
    </UserProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
  },
});
