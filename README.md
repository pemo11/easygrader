04/24/22

# simpelgrader
A simple Python application for grading Java assignments by running defined actions and tests for each submission

I started the development as part of my bachelor thesis about auto grading programming assignments because I felt there is a need for such a tool.

Wait, another autograder? Aren't there already a couple dozens (or maybe several hundreds) available for more than at least a decade? Why another one? And why as an old fashioned Python console application? And no GPT3 (Open AI)?

My thoughts were exactly the same;) - I definitely did not want to add another auto grader to the menue list. There are very good and well established applications like Praktomat, Graja, GATE, JACK and others and there are Moodle plugins like Coderunner or VirtualProgrammingLab which are all very good.

But I saw couple of short comings:

- Many applications are complex
- Some graders offer too many functions
- Not every autograder api is very well documented
- Some autograders are old (which is not automatically bad of course)
- Not very autograder is an Open Source project on GitHub, GitLab etc
- Not every institution uses Moodle
- And: When autograding a lot of assignments everything may start with a huge zip file

With SimpelGrader I'll try to address a few of these shortcommings:

- Processing a single zip file that contains all the assignments
- A small project that should be easy to understand
- Hopefully the whole source code is documented
- I will try to improve the application in the near future

But most important: SimpelGrader is not a complete autograder. It only runs prefined actions associated with each submission file through a xml file.

At the moment there is no real feedback mechanismen and no means to adapt the weighting of points for each action or test.

And SimpelGrader only works with simple Java assignments where the task always is to write a console application that does certain things and outputs something.

But again, SimpelGrader is not an autograder.

So, what is it good for?

At the moment SimpelGrader is for teachers or assistants of teachers of Java programming classes whose task is it to grade programming assigments that had been uploaded in a Moodle course as zip files.

SimpleGrader will process the single zip downloaded from Moodle, extract its content into directories, checks for completeness, stores everything in a small database and process each submission by running predefined actions like Java compile, a Checkstyle test or a JUnit test.

The result of each action/test will be stored in the database and displayed as an HTML report in the browser.

The idea is that SimpelGrader will hopefully save a lot of time because each zip file does not need to be extracted and each Java file does not have to load into Eclipse just to check if it compiles and to run Checkstyle.

The assistant/teacher still has to look at the source code, may be rerun tests, run additional tests and have to do the grading and write a feedback for the student.

But since the boring and error prone tasks are already done, there should be more time and energy left for the important parts:

- To really look at the solution
- May be Check for plagiarism
- Write a formative feedback

SimpelGrader is easy to install. I developed the application on Windows but it should run with no problemo on Linux and MacOS.

Python 3.8 is a requirement because I wanted to use a nice improvements for while loops.

SimpelGrader cannot run out of the box because two things have to be prepared first:

1. the grading xml file
2. the settings in simpelgrader.ini
3. Some Python packages (like lxml) have to be installed first (there is a requirements.txt of course)

Preparing the xml file can be time consuming because it means to define for each exercise a name, the name of the needed files, and additional actions and tests if compile and checkstyle is not enough.

The sample grade xml file is a template for a customized grading plan.

Step 2 is about writing the path of some directories and the name of the semester and the module in the ini file.

If everything is setup, SimpelGrader runs as any Python console application. A grade run will take a couple of minutes and ends always with showing a couple of report files.

*** more to follow soon ***

