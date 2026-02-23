var url = "http://www.google.com";

const EventEmitter = require("events");
const emitter = new EventEmitter();

function log(message) {
  console.log(message);
  emitter.emit("messageLogged", { id: 1, url: "http://google.com" });
}

module.exports.logger = log;
module.exports.endPoint = url;

emitter.on("messageLogged", (args) => {
  console.log("Listener called", args);
});

class Logger extends EventEmitter {
  log(message) {
    console.log(message);
    emitter.emit("messageLogged", { id: 1, url: "http://google.com" });
  }
}

module.exports = Logger;
