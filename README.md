04/24/22

# simpelgrader
A simple Python application for grading Java assignments by running defined actions and tests for each submission

## about the programm
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

Preparing the xml file can be a little time consuming because it means to define for each exercise a name, the name of the needed files, and additional actions and tests if compile and checkstyle is not enough.

The sample grade xml file gradingplan1.xml in the sampledata directory is a template for a customized grading plan.

Step 2 is about writing the path of some directories and the name of the semester and the module in the ini file.

If everything is setup, SimpelGrader runs as any Python console application. A grade run will take a couple of minutes and ends always with showing a couple of report files.

## getting started

First clone the repository into an subdirectory of the current directory 

`git clone https://github.com/pemo11/simpelgrader`

Create a virtual enviroment (not necessary but recommended)

`python -m venv .env`

Activate the virtual environment

`.env/scripts/activate`

install the (few= requirements)

`pip -r requirements.txt`

In PyCharm its necessary to choose either the Python interpreter from the newly created environment or choose any other Python 3.8 or above interpreter.

Altough it is not possible to start SimpelGrader without preparing the pathes in Simpelgrader.ini it is possible to start the application without any errors.

After the start the application menue is shown.

![Simpelgrader start menue](images/simpelgrader_01.png "Simpelgrader start menue")

The only possible options without editing Simpelgrader.ini are A for the precheck and H for showing the current log file.

### editing Simpelgrader.ini

Editing Simpelgrader.ini means providing the pathes for the several directories that Simpelgrader uses.

Currently they are nine different pathes that have to be set.

![Simpelgrader Simpelgrader.ini](images/simpelgrader_02.png "Simpelgrader Simpelgrader.ini")

Setting| Path of...                                      |Sample value
---|-------------------------------------------------|---
javaCompilerPath| the java compiler program file                  |E:\\Java\\jdk-11.0.14+9\\bin\\javac
javaLauncherPath | the java launcher program file                  |E:\\Java\\jdk-11.0.14+9\\bin\\java
jUnitPath| the two JUnit 4.x jar files                     |C:\\JUnit
gradingPlanPath| the xml file with the grading plan              |E:\\Grader-Helper\\CreateSimpelGraderSubmission\\gradingplan1.xml
submissionPath| the zip file that contains the submissions      |E:\\Grader-Helper\\CreateSimpelGraderSubmission\\Submissions
checkstylePath| the directory with the checkstyle jar file      |E:\\Checkstyle\\checkstyle-8.23-all.jar
checkstyleRulePath| the path of the checkstyle rule file            |E:\\Praktomat-Testpool\\GP1\\checkstyle-OMI3d.xml
studentRosterPath| the path of the csv file with the student names |E:\\Grader-Helper\\CreateSimpelGraderSubmission\\Student_Roster.csv
dbPath| the path of the sqlite db database file         |E:\\Projekte\\simpelgrader\\simpelgraderv1.db

the next table contain the other settings which are all optional

section|setting|meaning
---|---|---
run|gradeSemester|Name of the semester (just for the report)
run|gradeModule|Name of the module (just for the report)
run|gradingOperator|Name of the user (just of the report)
start|deleteSubmissionTree|Yes = delete all already extracted zip files first
start|deleteLogFile|Yes = start with a new log file each time
start|databaseBackup|make a copy of the db file before quitting the program

### editing the grading plan

the grading plan is a simple xml file that contains a task element for each exercise:

```
<sig:tasks xmlns:sig="urn:simpelgrader">
  <sig:task id="1000" exercise="EA1" title="Aufgabe EA1">
    <sig:description>description for task 1000</sig:description>
    <sig:files>
      <sig:file>App.java</sig:file>
      <sig:file>AppTest.java</sig:file>
    </sig:files>
    <sig:actions>
      <sig:action id="A01" active="True" type="java-compile">compile java file</sig:action>
    </sig:actions>
    <sig:tests>
      <sig:test id="T01" active="True">
        <sig:test-type>checkstyle</sig:test-type>
        <sig:test-description>Checkstyle-Überprüfung mit Omi-Regeln</sig:test-description>
        <sig:test-driver></sig:test-driver>
        <sig:test-score>1</sig:test-score>
      </sig:test>
    </sig:tests>
  </sig:task>
  ...

</tasks>
```

There is a naming convention for the java files:

**If the name ends with "Test" (like AppTest.java) the file will be threated as a JUnit file**

Each task element (exercise) contains a list of files, actions and tests.

Each action or test can be active or not. If a action or test is not active it will be omitted during a grading run.

There is a sample xml file in the sample directory. The only thing that needs to change are the name of exercises because this names have to be part of the file name for every submission.

**Example**: the name of an exercise is EA1. This means that each submitted zip file has to follow the simple naming scheme:

*EA1_FirstName_LastName.zip*

Withouth a task-element with exercise="EA1" Simpelgrader would not process this submission.

List of actions
- compile

List of tests
- checkstyle
- junit
- textcompare
- testdriver

The type names in the xml file are **not** case sensitive.
