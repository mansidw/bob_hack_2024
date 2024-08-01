import React, { useContext, useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import {
  Bubble,
  GiftedChat,
  InputToolbar,
  Avatar,
  Send,
  Message,
} from "react-native-gifted-chat";
import axios from "axios";
import { Image } from "react-native";
import { IconButton } from "react-native-paper";
import { UserContext } from "../UserContext";

const Chatbot = () => {
  const [message, setMessage] = useState([]);
  const { user } = useContext(UserContext);

  useEffect(() => {
    const initialMessage = {
      _id: Math.random().toString(),
      text: `Hi ${user.email}, I am BOBBandhu How can I assist you today?`,
      createdAt: new Date(),
      user: {
        _id: 2,
        name: "Bot",
      },
    };

    setMessage([initialMessage]);
  }, []);

  const handleSend = async (newMessage = []) => {
    try {
      // Get user message
      const userMessage = newMessage[0];

      setMessage((previousMessages) =>
        GiftedChat.append(previousMessages, userMessage)
      );
      const messageText = userMessage.text.toLowerCase();

      const response = await axios.post(
        `https://gray-coast-223cd0ba7ef947b6887c35bf094bde64.azurewebsites.net/api/chatbot`,
        {
          question: messageText,
        }
      );

      console.log("res", response);
      const recipe = response.data.answer;
      console.log(recipe);
      const botMessage = {
        _id: new Date().getTime + 1,
        text: recipe,
        createdAt: new Date(),
        user: {
          _id: 2,
          name: "BOB Bhandu",
        },
      };
      setMessage((previousMessages) =>
        GiftedChat.append(previousMessages, botMessage)
      );
    } catch (err) {
      console.log(err);
    }
  };

  const renderBubble = (props) => {
    return (
      <Bubble
        {...props}
        wrapperStyle={{
          right: {
            backgroundColor: "#F26522", // Orange color for user message
          },
          left: {
            backgroundColor: "#f0f0f0",
          },
        }}
        textStyle={{
          right: {
            color: "#fff", // White text for user message
          },
          left: {
            color: "#000",
          },
        }}
      />
    );
  };

  const renderAvatar = (props) => {
    if (props.currentMessage.user._id === 2) {
      // Customize bot avatar
      return (
        <View style={styles.botAvatarContainer}>
          <Image
            source={require("../assets/bobLogo.png")}
            style={styles.botAvatar}
          />
        </View>
      );
    }
    return <Avatar {...props} />;
  };

  const renderSend = (props) => {
    return (
      <Send {...props}>
        <View style={styles.sendingContainer}>
          <IconButton icon="send-circle" size={28} color="#fff" />
        </View>
      </Send>
    );
  };

  const renderInputToolbar = (props) => {
    return (
      <InputToolbar
        {...props}
        containerStyle={styles.inputToolbar}
        primaryStyle={styles.inputToolbarPrimary}
      />
    );
  };

  const renderMessage = (props) => {
    const { currentMessage } = props;
    if (currentMessage.user._id === 2) {
      return (
        <View style={styles.customMessageContainer}>
          <Image
            source={{
              uri: "https://geekrobocook.com/wp-content/uploads/2021/03/12.-Grilled-Paneer.jpg",
            }}
            style={styles.customMessageImage}
          />
          <Text style={styles.customMessageText}>{currentMessage.text}</Text>
        </View>
      );
    }
    return <Message {...props} />;
  };

  return (
    <View style={styles.container}>
      <GiftedChat
        messages={message}
        onSend={(newMessage) => handleSend(newMessage)}
        user={{ _id: 1 }}
        renderBubble={renderBubble}
        renderSend={renderSend}
        renderInputToolbar={renderInputToolbar}
        // renderMessage={renderMessage}
        renderAvatar={renderAvatar}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginBottom: 20,
    padding: 20,
    backgroundColor: "#fff",
  },
  button: {
    width: 370,
    marginTop: 10,
  },
  botAvatarContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 2,
    borderColor: "#F26522", // Orange border
    backgroundColor: "#F26522",
    justifyContent: "center",
    alignItems: "center",
    overflow: "hidden",
  },
  botAvatar: {
    width: "90%",
    height: "90%",
    objectFit: "contain",
    borderRadius: 50,
    backgroundColor: "#F26522",
  },
  sendingContainer: {
    justifyContent: "center",
    alignItems: "center",
    // marginRight: 10,
    borderColor: "#fff",
    borderWidth: 0,
    backgroundColor: "#f26522",
    width: "auto",
    height: 40,
    borderRadius: 10,
  },
  inputToolbar: {
    borderTopWidth: 2,
    borderRadius: 12,
    margin: 0,
    borderColor: "#e0e0e0",
    borderWidth: 2,
  },
  inputToolbarPrimary: {
    alignItems: "center",
  },
  customMessageContainer: {
    flexDirection: "column",
    alignItems: "left",
    padding: 10,
    backgroundColor: "#f0f0f0",
    borderRadius: 10,
    marginBottom: 5,
    maxWidth: "80%",
    textAlign: "left",
  },
  customMessageImage: {
    width: "100%",
    height: 100,
    borderRadius: 10,
    marginBottom: 5,
  },
});

export default Chatbot;
