const fs = require("fs");
files = fs.readdirSync(".");

console.log(files);

fs.readdir(".", function (error, files) {
  if (error) {
    console.log(error);
  } else {
    console.log(files);
  }
});

// global objects

console.log("first");

setTimeout(() => {
  console.log("first");
}, 1000);

clearTimeout();

// setInterval(() => {
//   console.log("first");
// }, 1000);

clearInterval();
