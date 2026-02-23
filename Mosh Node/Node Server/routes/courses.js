const express = require("express");
const router = express.Router();
const Joi = require("joi");

const courses = [
  { id: 1, name: "course1" },
  { id: 2, name: "course2" },
  { id: 3, name: "course3" },
];

router.get("/", (req, res) => {
  res.send(courses);
});

router.get("/:id", (req, res) => {
  const course = courses.find((c) => c.id === parseInt(req.params.id));
  if (!course) {
    res.status(404);
    return res.send("Course not found");
  } else {
    res.send(course);
  }
});

router.get("/random/:year/:month", (req, res) => {
  res.send(req.params);
});

router.get("/random/", (req, res) => {
  res.send(req.query);
});

router.post("/", (req, res) => {
  const schema = Joi.object({
    name: Joi.string().min(3).required(),
  });

  const { error } = schema.validate(req.body);

  if (error) {
    return res.status(400).send(error.details[0].message);
  } else {
    const course = {
      id: courses.length + 1,
      name: req.body.name,
    };

    courses.push(course);
    res.send(courses);
  }
});

router.put("/:id", (req, res) => {
  let course = courses.find((c) => c.id === parseInt(req.params.id));
  const schema = Joi.object({
    name: Joi.string().min(3).required(),
  });
  const { error } = schema.validate(req.body);

  if (error) {
    return res.status(400).send(error.details[0].message);
  }

  course.name = req.body.name;
  res.send(courses);
});

router.delete("/:id", (req, res) => {
  const course = courses.find((c) => c.id === parseInt(req.params.id));
  if (!course) {
    res.status(404);
    return res.send("Course not found");
  }

  const index = courses.indexOf(course);
  courses.splice(index, 1);
  res.send(courses);
});

module.exports = router;
