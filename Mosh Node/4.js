// (function (exports, require, module, __filename, __dirname) {
//   var url = "http://www.google.com";

//   function log(message) {
//     console.log(message);
//   }

//   module.exports = log;
// });

console.log(__filename);
console.log(__dirname);

var url = "http://www.google.com";

const eventEmitter = require("events");
const emitter = new eventEmitter();

emitter.on("messageLogged", (args) => {
  console.log("Listener called", args);
});

const log = function (message) {
  console.log(message);
  emitter.emit("messageLogged", { id: 1, url: "http://google.com" });
};

module.exports = log;
