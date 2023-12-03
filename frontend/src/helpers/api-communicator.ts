import axios from "axios";
import { useState } from "react";
import {io} from "socket.io-client";

type User = {
  name: string;
  email: string;
};

type LoginRes = {
  status?: number;
  data?: User;
}

type ChatData = {
  chats: string;
}
type ChatRes = {
  status?: number;
  data: ChatData;
}

const socket = io("http://127.0.0.1:6968/")
export const loginUser = async (email: string, password: string) => {
  socket.emit("login", {"username": email, "password": password});
  const res: LoginRes = await new Promise((resolve, reject) => {
    socket.on("login", (response) => {
      resolve(response);

    });
  });
  console.log(res)
  if (res.status !== 200) {
    throw new Error("Unable to login");
  }
  const data = await res.data;
  return data;
};

export const signupUser = async (
  name: string,
  email: string,
  password: string
) => {
  // const res = await axios.post("/user/signup", { name, email, password });
  socket.emit("signup", {"name": name, "username": email, "password": password});

  const res: LoginRes = await new Promise((resolve, reject) => {
    socket.on("signup", (response) => {
      resolve(response);
    });
  });

  if (res.status !== 200) {
    throw new Error("Unable to Signup");
  }
  const data = await res.data;
  return data;
};

export const checkAuthStatus = async () => {
  socket.emit("auth", "checkthisuser");
  
  const res: LoginRes = await new Promise((resolve, reject) => {
    socket.on("auth", (response) => {
      resolve(response);
    });
  });
  console.log(res);
  if (res.status !== 200) {
    throw new Error("Unable to authenticate");
  }
  const data = await res.data;
  return data;
};

export const sendChatRequest = async (message: string) => {
  socket.emit("chat", {"message": message});

  const res: ChatRes = await new Promise((resolve) => {
    socket.on("chat", (response) => {
      resolve(response);
    });
  });

  if (res.status !== 200) {
    throw new Error("Unable to send chat");
  }
  const data = await res.data;
  console.log(data);
  return data;
};

export const getUserChats = async () => {
  const res = await axios.get("/chat/all-chats");
  if (res.status !== 200) {
    throw new Error("Unable to send chat");
  }
  const data = await res.data;
  return data;
};

export const deleteUserChats = async () => {
  // const res = await axios.delete("/chat/delete");

  if (res.status !== 200) {
    throw new Error("Unable to delete chats");
  }
  const data = await res.data;
  return data;
};

export const logoutUser = async () => {
  console.log("log outttttttttttttttttttt");
  // const res = await axios.get("/user/logout");
  socket.emit("logout", "logout");

  const res: ChatRes = await new Promise((resolve) => {
    socket.on("logout", (response) => {
      resolve(response);
    });
  });
  
  console.log(res)
  if (res.status !== 200) {
    throw new Error("Unable to delete chats");
  }
  const data = await res.data;
  return data;
};
