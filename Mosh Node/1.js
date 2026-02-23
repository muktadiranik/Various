function logger(message) {
  console.log(message);
}

const EventEmitter = require("events");
const emitter = new EventEmitter();

// register a listener
emitter.on("messageLogged", (args) => {
  console.log("Listener called", args);
  emitter.emit("messageLogged", { id: 2, url: "http://google.com" });
});

class Logger extends EventEmitter {
  log(message) {
    console.log(message);
    this.emit("messageLogged", { id: 2, url: "http://google.com" });
  }
}

module.exports = Logger;
