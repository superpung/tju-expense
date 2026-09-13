import "@fontsource-variable/geist";
import "@fontsource-variable/geist-mono";
import "./styles/geist-tokens.css";
import "./styles/globals.css";
import "./styles/components.css";

import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import { initTheme } from "./lib/theme";

initTheme();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
