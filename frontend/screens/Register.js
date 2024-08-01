import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
} from "react-native";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";
import { SafeAreaView } from "react-native-safe-area-context";

const Register = ({ navigation }) => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const onHandleSignup = async () => {
    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );
      const user = userCredential.user;
      // const userRef = doc(database, "users", user.uid);
      // await setDoc(userRef, {
      //   displayName: name,
      //   email: email,
      //   uid: user.uid,
      //   photoURL: imageURL,
      //   phoneNumber: "",
      // });
      Alert.alert("Registered successfully!!!");
      navigation.navigate("Login");
    } catch (error) {
      Alert.alert(error.message);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.whiteSheet} />

      <Text style={styles.title}>Sign Up</Text>

      <SafeAreaView style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="Enter name"
          autoCapitalize="none"
          autoCorrect={false}
          textContentType="name"
          value={name}
          onChangeText={(text) => setName(text)}
        />
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

        <TouchableOpacity style={styles.button} onPress={onHandleSignup}>
          <Text style={styles.buttonText}>Sign Up</Text>
        </TouchableOpacity>

        <View style={styles.loginTextContainer}>
          <Text style={styles.loginText}>Don't have an account? </Text>
          <TouchableOpacity onPress={() => navigation.navigate("Login")}>
            <Text style={styles.loginLink}>Log In</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
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
  loginTextContainer: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "center",
    marginTop: 20,
  },
  loginText: {
    color: "gray",
    fontWeight: "600",
    fontSize: 14,
  },
  loginLink: {
    color: "#F26522",
    fontWeight: "600",
    fontSize: 14,
  },
});

export default Register;
