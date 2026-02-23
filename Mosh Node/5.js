const os = require("os");

console.log(os.platform())
console.log(os.release())

console.log(os.totalmem())
console.log(os.freemem())

console.log(`Total Memory: ${os.totalmem()}, Free Memory: ${os.freemem()}`)


const path = require("path")

console.log(path.parse(__filename))