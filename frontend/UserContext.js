// UserContext.js
import React, { createContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { auth } from "./firebase";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { unregisterIndieDevice } from "native-notify";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUser = await AsyncStorage.getItem("user");
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error("Failed to load user from AsyncStorage", error);
      } finally {
        setLoading(false);
      }
    };

    loadUser();

    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
        AsyncStorage.setItem("user", JSON.stringify(currentUser));
      } else {
        setUser(null);
        AsyncStorage.removeItem("user");
      }
    });

    return () => unsubscribe();
  }, []);

  const logout = async () => {
    await signOut(auth);
    unregisterIndieDevice(user.uid, 22691, "GNcqpcDMoJaUg3CZA7HF9Q");
    setUser(null);
    AsyncStorage.removeItem("user");
  };

  return (
    <UserContext.Provider value={{ user, setUser, logout }}>
      {!loading && children}
    </UserContext.Provider>
  );
};
