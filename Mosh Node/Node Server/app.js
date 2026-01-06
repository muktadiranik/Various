const startupDebugger = require("debug")("app:startup");
const databaseDebugger = require("debug")("app:database");
const Joi = require("joi");
const logger = require("./middleware/logger");
const express = require("express");
const app = express();
const helmet = require("helmet");
const morgan = require("morgan");
const config = require("config");
const courses = require("./routes/courses");
const root = require("./routes/root");

app.set("view engine", "pug");
app.set("views", "./views");

console.log(`NODE_ENV: ${process.env.NODE_ENV}`);
console.log(`app: ${app.get("env")}`);

console.log(`Application Name: ${config.get("name")}`);
console.log(`Mail Server: ${config.get("mail.host")}`);
console.log(`Mail Password: ${config.get("mail.password")}`);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));
app.use(helmet());
app.use(morgan("tiny"));
app.use("/courses/", courses);
app.use("/", root);

if (app.get("env") === "development") {
  console.log("development");
  startupDebugger("Debugging");
} else {
  console.log("production");
}

databaseDebugger("Connected to database");

app.use(function (req, res, next) {
  console.log("logging");
  next();
});

app.use((req, res, next) => {
  console.log("Authenticating");
  next();
});

app.use(logger);

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
