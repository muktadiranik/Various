const GREETING = "Hello";
let count = 10;
var isActive = true;

const numbers = [1, 2, 3, 4, 5];
console.log(
  numbers,
  numbers.map((num) => num * num)
);
console.log(
  numbers,
  numbers.filter((num) => num > 1)
);

let doubled = numbers.map((num) => num * 2);
console.log(doubled);

console.log(doubled.reduce((acc, current) => acc * current, 1));

// Object
const user = {
  firstName: "Alex",
  lastName: "Smith",
  age: 30,
  address: "123 Main St",
};

const { firstName, age } = user;
console.log(firstName, age);

const updatedUser = { ...user, age: 31, email: "qYf7o@example.com" };
console.log(updatedUser);

async function fetchData(data) {
  console.log("fetching data");

  await new Promise((resolve) => setTimeout(resolve, 100));
}

fetchData("Financials");
