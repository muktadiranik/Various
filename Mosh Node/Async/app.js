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

function getUser(id, callback) {
  setTimeout(() => {
    console.log("Reading a user from database...");
    callback({ id: id, gitHubUserName: "mosh" });
  }, 200);
}

function getRepositories(userName, callback) {
  setTimeout(() => {
    console.log("Calling GitHub API...");
    callback(["repo1", "repo2", "repo3"]);
  }, 200);
}

function getCommits(repo, callback) {
  setTimeout(() => {
    console.log("Fetching commits for", repo);
    callback(["commit1", "commit2", "commit3"]);
  }, 200);
}

function displayCommits(commits) {
  console.log("Commits:", commits);
}

console.log("before");
getUser(1, getRepositoriesFromUser);
console.log("after");

function getRepositoriesFromUser(user) {
  getRepositories(user.gitHubUserName, getCommitsFromRepo);
}

function getCommitsFromRepo(repos) {
  getCommits(repos[0], displayCommits);
}

function displayCommits(commits) {
  console.log("Commits:", commits);
}

function getUser(id, callback) {
  return new Promise((resolve) => {
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
getUser(1)
  .then((user) => {
    return getRepositories(user.gitHubUserName);
  })
  .then((repos) => {
    return getCommits(repos[0]);
  })
  .then((commits) => {
    displayCommits(commits);
  })
  .catch((error) => {
    console.log("Error:", error.message);
  });
console.log("after");

console.log("before");
getUser(1)
  .then(getRepositories)
  .then(getCommits)
  .then(displayCommits)
  .catch((error) => console.log(error.message));
console.log("after");


const p = getUser(1);
p.then((user) => console.log(user));
