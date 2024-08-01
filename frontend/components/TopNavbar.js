// TopNavbar.js
import React, { useContext } from "react";
import { View, Text, Button, StyleSheet } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { UserContext } from "../UserContext";

const TopNavbar = () => {
  const { user, logout } = useContext(UserContext);
  const navigation = useNavigation();

  const handleLogout = () => {
    logout();
    navigation.navigate("Login");
  };

  return (
    <View style={styles.navbar}>
      <Text style={styles.title}>BOBBhandu</Text>
      {user ? (
        <Button
          style={styles.logOutButton}
          title="Logout"
          color= "white"
          onPress={handleLogout}
        />
      ) : (
        <View style={styles.authButtons}>
          <Button
            title="Sign In"
            onPress={() => navigation.navigate("Login")}
          />
          <Button
            title="Sign Up"
            onPress={() => navigation.navigate("Register")}
          />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  navbar: {
    height: 60,
    backgroundColor: "#F26522",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderColor: "#fff",
    position: "absolute",
    top: 60, // Position it at the bottom
    left: 0,
    right: 0,
    zIndex: 1000, // High z-index to ensure it's above other elements
  },
  title: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "bold",
  },
  authButtons: {
    flexDirection: "row",
    gap: 10,
  },
});

export default TopNavbar;
