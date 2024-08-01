// Login.js
import React, { useState, useContext } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
  StatusBar,
} from "react-native";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";
import { SafeAreaView } from "react-native-safe-area-context";
import { UserContext } from "../UserContext";
import { registerIndieID } from "native-notify";
import AsyncStorage from "@react-native-async-storage/async-storage";

const Login = ({ navigation }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { setUser } = useContext(UserContext);

  const onHandleLogin = async () => {
    if (email !== "" && password !== "") {
      signInWithEmailAndPassword(auth, email, password)
        .then(async (res) => {
          await AsyncStorage.setItem("user", JSON.stringify(res.user));
          setUser(res.user);
          Alert.alert("Login success");
          registerIndieID(res.user.uid, 22691, "GNcqpcDMoJaUg3CZA7HF9Q");
          navigation.navigate("Home");
        })
        .catch((err) => Alert.alert("Login error", err.message));
    } else {
      Alert.alert("Please enter email and password");
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.whiteSheet} />

      <Text style={styles.title}>Log In</Text>

      <SafeAreaView style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="Enter email"
          autoCapitalize="none"
          keyboardType="email-address"
          textContentType="emailAddress"
          autoFocus={true}
          value={email}
          onChangeText={(text) => setEmail(text)}
        />
        <TextInput
          style={styles.input}
          placeholder="Enter password"
          autoCapitalize="none"
          autoCorrect={false}
          secureTextEntry={true}
          textContentType="password"
          value={password}
          onChangeText={(text) => setPassword(text)}
        />

        <TouchableOpacity style={styles.button} onPress={onHandleLogin}>
          <Text style={styles.buttonText}>Log In</Text>
        </TouchableOpacity>

        <View style={styles.signupTextContainer}>
          <Text style={styles.signupText}>Don't have an account? </Text>
          <TouchableOpacity onPress={() => navigation.navigate("Register")}>
            <Text style={styles.signupLink}>Sign Up</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
      <StatusBar barStyle="light-content" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    justifyContent: "center",
    padding: 20,
  },
  whiteSheet: {
    width: "100%",
    height: "100%",
    position: "absolute",
    top: 0,
    left: 0,
    backgroundColor: "#fff",
    borderTopLeftRadius: 60,
    borderTopRightRadius: 60,
    zIndex: -1,
  },
  title: {
    fontSize: 36,
    fontWeight: "bold",
    color: "#F26522",
    alignSelf: "center",
    paddingBottom: 24,
  },
  form: {
    width: "100%",
    alignSelf: "center",
  },
  input: {
    backgroundColor: "#f6f7fb",
    height: 58,
    marginBottom: 20,
    fontSize: 16,
    borderRadius: 10,
    padding: 12,
  },
  button: {
    backgroundColor: "#F26522",
    height: 58,
    borderRadius: 10,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 20,
  },
  buttonText: {
    fontWeight: "bold",
    color: "#fff",
    fontSize: 18,
  },
  signupTextContainer: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "center",
    marginTop: 20,
  },
  signupText: {
    color: "gray",
    fontWeight: "600",
    fontSize: 14,
  },
  signupLink: {
    color: "#F26522",
    fontWeight: "600",
    fontSize: 14,
  },
});

export default Login;
