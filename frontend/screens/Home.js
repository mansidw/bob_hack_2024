import React, { useContext, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Button,
  TouchableOpacity,
  Image,
  TextInput,
  Alert,
  TouchableWithoutFeedback,
  Keyboard,
} from "react-native";
import { UserContext } from "../UserContext";
import TopNavbar from "../components/TopNavbar";
import botIcon from "../assets/bobLogo.png"; // Make sure to add an appropriate bot icon image
import axios from "axios";

const Home = ({ navigation }) => {
  const { user } = useContext(UserContext);
  const [irctc, setIrctc] = useState(0);
  const [snapdeal, setSnapdeal] = useState(0);

  const handleIrctc = async () => {
    Alert.alert(
      "Success",
      `This is a confirmation that \nRs. ${irctc} transaction is completed on IRCTC`
    );

    try {
      const response = await axios.post(
        `https://gray-coast-223cd0ba7ef947b6887c35bf094bde64.azurewebsites.net/api/trigger-transaction`,
        [
          {
            user_id: "3iT4Ld86j4iLkfmQjNtj",
            transaction_date: new Date(),
            product_category: "shopping",
            remarks: "online shopping on irctct",
            price: irctc,
          },
        ],
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
    } catch (err) {
      console.log(err);
    }
  };

  const handleSnapdeal = async () => {
    Alert.alert(
      "Success",
      `This is a confirmation that \nRs. ${snapdeal} transaction is completed on Snapdeal`
    );

    try {
      const response = await axios.post(
        `https://gray-coast-223cd0ba7ef947b6887c35bf094bde64.azurewebsites.net/api/trigger-transaction`,
        [
          {
            user_id: "3iT4Ld86j4iLkfmQjNtj",
            transaction_date: new Date(),
            product_category: "shopping",
            remarks: "online shopping on snapdeal",
            price: snapdeal,
          },
        ],
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <TouchableWithoutFeedback onPress={() => Keyboard.dismiss()}>
      <View style={styles.container}>
        {user ? (
          <>
            <Text>Welcome, {user.email}</Text>
          </>
        ) : (
          <Text>Welcome to MyApp. Please sign in or sign up.</Text>
        )}

        <TouchableOpacity
          style={styles.botIcon}
          onPress={() => navigation.navigate("BOBBhandu")}
        >
          <Image source={botIcon} style={styles.botIconImage} />
        </TouchableOpacity>

        {/* IRCTC Section */}
        <View style={styles.paymentContainer}>
          <Text style={styles.paymentHeader}>IRCTC</Text>
          <View style={styles.paymentComibiner}>
            <TextInput
              style={styles.paymentInput}
              placeholder="Enter irctc amount"
              keyboardType="numeric"
              value={irctc}
              onChangeText={setIrctc}
            />
            <TouchableOpacity style={styles.apiButton} onPress={handleIrctc}>
              <Text style={styles.apiButtonText}>Submit</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.paymentContainer}>
          <Text style={styles.paymentHeader}>Snapdeal</Text>
          <View style={styles.paymentComibiner}>
            <TextInput
              style={styles.paymentInput}
              placeholder="Enter Snapdeal amount"
              keyboardType="numeric"
              value={snapdeal}
              onChangeText={setSnapdeal}
            />
            <TouchableOpacity style={styles.apiButton} onPress={handleSnapdeal}>
              <Text style={styles.apiButtonText}>Submit</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </TouchableWithoutFeedback>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    // justifyContent: "center",
    // alignItems: "center",
    padding: 20,
    marginTop: 20,
    backgroundColor: "#fff",
  },
  botIcon: {
    position: "absolute",
    bottom: 20,
    right: 20,
    backgroundColor: "#F26522", // Background color of the circle
    // borderRadius: 50, // Makes the icon circular
    padding: 10, // Size of the icon
    justifyContent: "center",
    alignItems: "center",
    elevation: 5, // Adds shadow effect (Android)
    shadowColor: "#000", // Shadow color (iOS)
    shadowOffset: { width: 0, height: 2 }, // Shadow offset (iOS)
    shadowOpacity: 0.3, // Shadow opacity (iOS)
    shadowRadius: 4, // Shadow blur radius (iOS)
  },
  botIconImage: {
    width: 50, // Width of the bot icon
    height: 50, // Height of the bot icon
    // borderRadius: 25, // Makes the image circular
  },
  paymentContainer: {
    marginTop: 20,
  },
  paymentHeader: {
    fontSize: 20,
    fontWeight: "bold",
  },
  paymentComibiner: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  paymentInput: {
    padding: 20,
  },
  apiButtonText: {
    color: "#fff",
    padding: 15,
  },
  apiButton: {
    backgroundColor: "#F26522",
    // borderRadius: "12",
  },
});

export default Home;
