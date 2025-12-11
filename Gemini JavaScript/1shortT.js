// A single code snippet illustrating Core JS, Functions, Arrays, Objects, and Async

// 1. Core Variables and Data Types
const GREETING = "Hello";
let count = 1;
let isActive = true;

// 2. Array Methods (Functional Programming)
const numbers = [10, 20, 30, 40];
const doubled = numbers
  .map((n) => n * 2) // [20, 40, 60, 80]
  .filter((n) => n > 50); // [60, 80]

const sum = doubled.reduce((acc, current) => acc + current, 0); // 140

// 3. Object Destructuring and Spread Syntax
const user = {
  firstName: "Alex",
  age: 30,
  address: { street: "Main St" },
};

const { firstName, age } = user;
const updatedUser = { ...user, age: age + 1 }; // Immutable update using spread

// 4. Async/Await (Simulating an API call)
async function fetchData(dataName) {
  console.log(`\n--- ${GREETING}, ${firstName}. ---`);
  console.log(`Starting to fetch ${dataName} for user aged ${updatedUser.age}...`);

  // Simulate a network delay
  await new Promise((resolve) => setTimeout(resolve, 500));

  // Demonstrate basic class and method usage (OOP)
  class Report {
    constructor(data) {
      this.data = data;
    }
    summarize() {
      return `Data processed: Array sum is ${this.data.sum}.`;
    }
  }

  const report = new Report({ sum: sum });

  return report;
}

// Immediately Invoked Async Function Expression (IIAFE) to run the code
(async () => {
  try {
    const reportObject = await fetchData("Financials");

    // Demonstrate Optional Chaining (Safely accessing properties)
    const street = user?.address?.street ?? "N/A";

    console.log(`\nResults:`);
    console.log(`Name: ${firstName}, Street: ${street}`);
    console.log(`Doubled Array Filtered: [${doubled.join(", ")}]`);
    console.log(reportObject.summarize());

    // Final State Check
    console.log(`\nFinal count: ${count++}`); // count is 2
    console.log(`Is Active: ${isActive}`);
  } catch (error) {
    console.error("An error occurred:", error);
  }
})();
