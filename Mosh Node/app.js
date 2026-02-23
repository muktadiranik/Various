function print_object(obj) {
  console.log(obj);
}

const obj = { a: 1, b: 2, c: 3 };
print_object(obj);

const EventEmitter = require("events");
const emitter = new EventEmitter();
emitter.on("messageLogged", function (args) {
  console.log("Listener called", args);
});

console.log(module);

const logger = require("./logger.js");
const logger1 = new logger();
logger1.log("Hello");

console.log(logger.endPoint);

const Logger = require("./1.js");
const logger2 = new Logger();
logger2.log("Hello");

const log = require("./4.js");

log("Hello");

const _ = require("underscore");

console.log(_.contains[(1, 2, 3)], 2);
