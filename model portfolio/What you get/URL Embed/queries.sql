-- 1. Create a table
CREATE TABLE students (
  id INT PRIMARY KEY,
  name VARCHAR(50),
  major VARCHAR(50),
  gpa DECIMAL(3,2)
);

-- 2. Insert sample data
INSERT INTO students (id, name, major, gpa) VALUES
(1, 'Alice', 'Computer Science', 3.8),
(2, 'Bob', 'Mathematics', 3.5),
(3, 'Charlie', 'Physics', 3.2);

-- 3. Query: Get all students with GPA > 3.4
SELECT * FROM students WHERE gpa > 3.4;
