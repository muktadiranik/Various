const mongoose = require("mongoose");

mongoose
  .connect("mongodb://localhost/mongo-exercises")
  .then(() => {
    console.log("Database connected successfully");
  })
  .catch((error) => {
    console.log("Error connecting to database:", error);
  });

const personSchema = new mongoose.Schema({
  name: String,
  age: Number,
  email: String,
});

const Person = mongoose.model("Person", personSchema, "persons");

async function getPerson() {
  const pageNumber = 1;
  const pageSize = 100;
  //   const persons = await Person.find().sort({ name: 1 }).select({ name: 1, email: 1 });
  //   const persons = await Person.find()
  //     .sort({ name: -1 })
  //     .select({ name: 1 })
  //     .skip((pageNumber - 1) * pageSize)
  //     .limit(pageSize);
  const persons = await Person.find({ name: /.*Doe.*/ })
    .sort({ name: 1 })
    .select({ name: 1, email: 1 });
  console.log(persons);
}

// getPerson();

async function createPerson() {
  const person = new Person({
    name: "John Doe",
    age: 30,
    email: "Bh9wZ@example.com",
  });

  const result = await person.save();
  console.log(result);
}

// createPerson();

async function createPersonsFromFile() {
  const fs = require("fs");
  const personsData = fs.readFileSync("D:\\Python\\Various\\Mosh Node\\Mongo\\data.json", "utf-8");
  const persons = JSON.parse(personsData);
  await Person.insertMany(persons);
  console.log("Persons created successfully from file");
}

// createPersonsFromFile();

const courseSchema = new mongoose.Schema({
  name: String,
  description: String,
  author: String,
  duration: String,
  level: String,
  tags: [String],
  price: Number,
});

const Course = mongoose.model("Course", courseSchema, "courses");

async function getCourses() {
  //   const courses = await Course.find();
  //   const courses = await Course.find().and([({ author: "Mosh" }, { duration: { $in: [8, 10] } })]);
  //   const courses = await Course.find().or([{ author: "Mosh" }, { price: { $in: [10, 15, 20] } }]);
  //   const courses = await Course.find()
  //     .and([{ author: /^Mosh/ }, { tags: { $all: ["JavaScript", "Node.js"] } }, {name: /.*by.*/}])
  //     .sort("-price")
  //     .select("name author price");
  const courses = await Course.find()
    .or([{ name: /.*course.*/ }, { price: { $gte: 15 } }, { author: /^Mosh/ }])
    .sort("-name")
    .select("name author price");
  console.log(courses);
}

// getCourses();

async function updateCourse(id) {
  const course = await Course.findById(id);
  course.set({
    name: "Updated Course Name",
    duration: "12 hours",
  });
  const result = await course.save();
  console.log(result);
}

// updateCourse("696678a76f190e291b58a416");

async function updateCourseDirectly(id) {
  const result = await Course.updateOne(
    { _id: id },
    {
      $set: {
        name: "Directly Updated Course Name",
        duration: "15 hours",
      },
    }
  );
  console.log(result);
}

// updateCourseDirectly("696a5152eaa9f0716bc680ed");

async function updateCourseFindAndUpdate(id) {
  const course = await Course.findByIdAndUpdate(
    id,
    {
      $set: {
        name: "Find and Update Course Name",
        duration: "20 hours",
      },
    },
    { new: true } // to return the updated document
  );
  console.log(course);
}

// updateCourseFindAndUpdate("696a5152eaa9f0716bc680ee");

async function createCoursesFromFile() {
  const fs = require("fs");
  const coursesData = fs.readFileSync("D:\\Python\\Various\\Mosh Node\\Mongo\\course.json", "utf-8");
  const courses = JSON.parse(coursesData);
  await Course.insertMany(courses);
  console.log("Courses created successfully from file");
}

// createCoursesFromFile();

async function removeCourse(id) {
  const result = await Course.findByIdAndDelete(id);
  console.log(result);
}

// removeCourse("696a5152eaa9f0716bc680ed");
