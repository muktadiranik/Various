import dotenv from "dotenv";

dotenv.config();

export const ENV = {
  BASE_URL: process.env.BASE_URL ?? "https://conduit.bondaracademy.com",

  API_URL: process.env.API_URL ?? "https://conduit-api.bondaracademy.com/api",

  EMAIL: process.env.EMAIL ?? "",

  PASSWORD: process.env.PASSWORD ?? "",
};

if (!ENV.EMAIL || !ENV.PASSWORD) {
  throw new Error("EMAIL and PASSWORD must be provided in the .env file.");
}

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  EDITOR: "/editor",
  SETTINGS: "/settings",
};

export const API_ROUTES = {
  LOGIN: "users/login",
  USER: "user",
  ARTICLES: "articles",
  TAGS: "tags",
};

export const TIMEOUTS = {
  SHORT: 5_000,
  MEDIUM: 10_000,
  LONG: 30_000,
};

export const STORAGE = {
  AUTH: "storage/auth.json",
};

export const ARTICLE = {
  DEFAULT_TAG: "playwright",
};

export const SELECTORS = {
  SUCCESS_ALERT: ".toast-success, .alert-success",
  ERROR_ALERT: ".toast-error, .alert-danger",
};

export const BROWSERS = {
  CHROMIUM: "chromium",
  FIREFOX: "firefox",
  WEBKIT: "webkit",
} as const;
