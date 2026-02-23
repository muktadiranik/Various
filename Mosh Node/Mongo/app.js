const mongoose = require("mongoose");

mongoose
  .connect("mongodb://localhost/playground")
  .then(() => {
    console.log("Database connected successfully");
  })
  .catch((error) => {
    console.log("Error connecting to database:", error);
  });

const courseSchema = new mongoose.Schema({
  name: String,
  author: String,
  tags: [String],
  date: { type: Date, default: Date.now },
  isPublished: Boolean,
});

const Course = mongoose.model("Course", courseSchema);

async function createCourse() {
  const course = new Course({
    name: "Node.js Course",
    author: "Mosh",
    tags: ["node", "javascript"],
    isPublished: true,
  });

  const result = await course.save();
  console.log(result);
}

// createCourse();

async function createBatchCourses() {
  const courses = [
    new Course({
      name: "Angular Course",
      author: "Mosh",
      tags: ["angular", "javascript"],
      isPublished: true,
    }),
    new Course({
      name: "React Course",
      author: "Mosh",
      tags: ["react", "javascript"],
      isPublished: true,
    }),
    new Course({
      name: "Vue Course",
      author: "Mosh",
      tags: ["vue", "javascript"],
      isPublished: true,
    }),
  ];

  const result = await mongoose.connection.collection("courses").insertMany(courses);
  console.log(result);
}

// createBatchCourses();

async function getCourses() {
  const pageNumber = 1;
  const pageSize = 10;

  const courses = await Course.find({ isPublished: true, author: "Mosh" })
    .skip((pageNumber - 1) * pageSize)
    .limit(5)
    .sort({ name: 1 })
    .select({ name: 1, tags: 1 });
  console.log(courses);
}

getCourses();

async function getFilteredCourses() {
  //   const courses = await Course.find({ price: { $gt: 10, $lte: 20 } });
  //   const courses = await Course.find({ price: { $in: [10, 15, 20] } });
  //   const courses = await Course.find().or([{ author: "Mosh" }, { isPublished: true }]);
  //   const courses = await Course.find().and([{ author: "Mosh" }, { isPublished: true }]);
  //   const courses = await Course.find().select({ name: 1, author: 1 });
  //   const courses = await Course.find({ author: /^Mosh/ }).find({ author: /Courses$/i });
  //   const courses = await Course.find({ author: /^Mosh/ });
  const courses = await Course.find({ author: /.*Mosh.*/i });
  console.log(courses);
}

// getFilteredCourses();

async function getCoursesCount() {
  const count = await Course.find().countDocuments();
  console.log("Total courses count:", count);
}

// getCoursesCount();

async function getPaginatedCourses() {
  const pageNumber = 1;
  const pageSize = 10;

  const courses = await Course.find()
    .skip((pageNumber - 1) * pageSize)
    .limit(pageSize);
  console.log(courses);
}

getPaginatedCourses();
