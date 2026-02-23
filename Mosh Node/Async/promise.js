const p = new Promise((resolve, reject) => {
  setTimeout(() => {
    resolve(1); // pending -> resolved
    console.log("Async operation complete");
  }, 200);
});

p.then((result) => {
  console.log("Result:", result);
});

const p1 = new Promise((resolve, reject) => {
  setTimeout(() => {
    console.log("Async operation in progress...");
    reject(new Error("Something went wrong")); // pending -> rejected
  }, 200);
});

p1.then((result) => {
  console.log("Result:", result);
}).catch((error) => {
  console.log("Error:", error.message);
});

// example

console.log("before");
getUser(1, (user) => {
  getRepositories(user.gitHubUserName, (repos) => {
    getCommits(repos[0], (commits) => {
      displayCommits(commits);
    });
  });
});
console.log("after");

// async functions

function getUser(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      console.log("Reading a user from database...");
      resolve({ id: id, gitHubUserName: "mosh" });
    }, 200);
  });
}

function getRepositories(userName) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      console.log("Calling GitHub API...");
      resolve(["repo1", "repo2", "repo3"]);
    }, 200);
  });
}

function getCommits(repo) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      console.log("Fetching commits for", repo);
      resolve(["commit1", "commit2", "commit3"]);
    }, 200);
  });
}

function displayCommits(commits) {
  console.log("Commits:", commits);
}

console.log("before");
getUser(1).then(getRepositories).then(getCommits).then(displayCommits);
console.log("after");

async function displayCommits() {
  try {
    const user = await getUser(1);
    const repos = await getRepositories(user.gitHubUserName);
    const commits = await getCommits(repos[0]);
    console.log(commits);
  } catch (error) {
    console.log("Error:", error.message);
  }
}

displayCommits();
