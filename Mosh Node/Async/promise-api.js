const p = Promise.resolve({ id: 1 });
p.then((result) => console.log(result));

const p2 = Promise.reject(new Error("Something went wrong"));
p2.catch((error) => {
  console.log(error);
  console.log(error.message);
});

const p3 = Promise.resolve(42);
p3.then((result) => console.log(result));

const p4 = new Promise((resolve) => {
  console.log("async operation 1");
  setTimeout(() => resolve(1), 200);
});

const promise1 = new Promise((resolve) => {
  setTimeout(() => {
    console.log("async operation 1");
    resolve(1);
  }, 200);
});

const promise2 = new Promise((resolve) => {
  setTimeout(() => {
    console.log("async operation 2");
    resolve(2);
  }, 200);
});

Promise.all([promise1, promise2])
  .then((result) => {
    console.log(result);
  })
  .catch((error) => {
    console.log("Error:", error.message);
  });

Promise.race([promise1, promise2])
  .then((result) => {
    console.log("Result:", result);
  })
  .catch((error) => {
    console.log("Error:", error.message);
  });
