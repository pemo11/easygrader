# Simpelgrader 0.8
last update: 05/06/2022

author: *Peter Monadjemi*

1. Prerequisites
2. Installation
3. Preparing the assignments
4. Preparing the grading xml file
5. Preparing Simpelgrader.ini
6. First start

## Prerequisites

The first (and only) requirement is Python version 3.8 or higher. 

## Preparation

*Simpelgrader* is simple, the involved programms are not that simple. To be able to use *Simpelgrader* for grading Java source files you will need some equipment:

- a Java SDK (eg. version 11 or 17)
- JUnit 4.x (two jar files)
- Checkstyle (one jar file)

For setting up *Simpelgrader.ini* you will need the directory pathes of the following files/directories:

- the Java Compiler (javac or javac.exe under Windows)
- the Java Launcher (java or java.exe under Windows)
- the JUnit directory path that contains junit-4.10.jar and hamcrest-core-1.3.jar
- the checkstyle directory that contains checkstyle-8.23-all.jar (or any other version that works with the rule file)
- a checkstyle rule file (the xml file that contains the checkstyle rules)

JavaC and Java must be part of the path so typing in "java" in the command window should start the Java launcher for example.

This is usually the case if the Java SDK had been installed properly.

For JUnit and Checkstyle there is no installation. There are just a couple of jar files that can be taken from any directory (or Maven Central).

## Installation

The first step is cloning the project repo:

`git clone https://github.com/pemo11/simpelgrader`

The next step is to install the Python packages needed for this application.

I recommend creating a Virtual Environment first because the installed packages won't interfere with the packages used by other Python applications on this computer.

If *Simpelgrader* will be the only Python application on this computer or package versions doesn't matter than you can skip this step.

Start *Simpelgrader* to check if everything is working:

`python .\Main.py`

The main (and only) menue appears (figure 1).

Choose **Menue option A** for checking the *simpelgrader.ini* settings.

None of the settings are valid at the moment. 

Choose **Menue option H** for showing the log file with the standard editor. There will be a entries with error messages.

## Setting up the grading.xml file

This step has to be done in a text editor (there might be a dialog editor in the near future like the very good ProFormA editor).

The general structure of the file looks like this:

```
<?xml version="1.0" encoding="utf-8"?>
<sig:tasks xmlns:sig="urn:simpelgrader">
 
</sig:tasks>
```

There has to be a *task* element for every exercise that should be graded.

Let's say the exercise name is EA1 (in German for Einsendeaufgabe 1).

I will include a *task* element for this exercise:

```
<?xml version="1.0" encoding="utf-8"?>
<sig:tasks xmlns:sig="urn:simpelgrader">
 <sig:task id="1000" exercise="EA1" title="Aufgabe EA1">
    <sig:description>description for task 1000</sig:description>
  </sig:task> 
</sig:tasks>
```

At the moment there is nothing of importance included in the *task* element.

First, I will include the files through the *files* element:

```
<?xml version="1.0" encoding="utf-8"?>
<sig:tasks xmlns:sig="urn:simpelgrader">
 <sig:task id="1000" exercise="EA1" title="Aufgabe EA1">
    <sig:description>description for task 1000</sig:description>
      <sig:files>
      <sig:file>App.java</sig:file>
      <sig:file>AppTest.java</sig:file>
      <sig:file>SchaltjahrTester.java</sig:file>
    </sig:files>
  </sig:task> 
</sig:tasks>
```

This means, that three files are expected with each submission of an EA1 assignment:

- App.java
- AppTest.java
- SchaltjahrTester.java

The next step is do define a compile action through the *actions* element and a *action* subelement:

```
<?xml version="1.0" encoding="utf-8"?>
<sig:tasks xmlns:sig="urn:simpelgrader">
 <sig:task id="1000" exercise="EA1" title="Aufgabe EA1">
    <sig:description>description for task 1000</sig:description>
    <sig:files>
      <sig:file>App.java</sig:file>
      <sig:file>AppTest.java</sig:file>
      <sig:file>SchaltjahrTester.java</sig:file>
    </sig:files>
```
&nbsp;&nbsp;&nbsp;&nbsp;<mark><sig:actions></br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<sig:action id="A01" active="True" type="java-compile">compile java file</sig:action></br>
&nbsp;&nbsp;&nbsp;&nbsp;</sig:actions><
</mark>
```
  </sig:task> 
</sig:tasks>
```

The id of the action is not important. The action has to be active and the type has to be "java-compile" (the type is not case sensitive).

The compile action will apply to all java files with the Java compiler referenced in *Simpelgader.ini*.

The next step is to add a checkstyle test through the *tests* element and a *test* subelement.

```
<?xml version="1.0" encoding="utf-8"?>
<sig:tasks xmlns:sig="urn:simpelgrader">
 <sig:task id="1000" exercise="EA1" title="Aufgabe EA1">
    <sig:description>description for task 1000</sig:description>
    <sig:files>
      <sig:file>App.java</sig:file>
      <sig:file>AppTest.java</sig:file>
      <sig:file>SchaltjahrTester.java</sig:file>
    </sig:files>
    <sig:actions>
      <sig:action id="A01" active="True" type="java-compile">compile java file</sig:action>
    </sig:actions>

    <sig:tests>
      <sig:test id="T01" active="True">
        <sig:test-type>checkstyle</sig:test-type>
        <sig:test-description>Checkstyle-Überprüfung mit Omi-Regeln</sig:test-description>
        <sig:test-score>1</sig:test-score>
      </sig:test>
     </sig:tests>

  </sig:task> 
</sig:tasks>
```

Like an action element a test have to be active (active="True"). The only important subelement is test-type. The value has to be "checkstyle".

Due to naming conventions defined in the programm code, only the App.java file will be checkstyled.

The test-score is 1 which is a more or less arbitrary value.

There are two more test-types avaiable:

- Junit
- Textcompare

The next step is to include another test, this time its a JUnit test, so *test-type* is "JUnit". The JUnit test class for this exercise is AppTest.java. It contains several test methods.

```
<?xml version="1.0" encoding="utf-8"?>
<sig:tasks xmlns:sig="urn:simpelgrader">
 <sig:task id="1000" exercise="EA1" title="Aufgabe EA1">
    <sig:description>description for task 1000</sig:description>
    <sig:files>
      <sig:file>App.java</sig:file>
      <sig:file>AppTest.java</sig:file>
      <sig:file>SchaltjahrTester.java</sig:file>
    </sig:files>
    <sig:actions>
      <sig:action id="A01" active="True" type="java-compile">compile java file</sig:action>
    </sig:actions>
    <sig:tests>
      <sig:test id="T01" active="True">
        <sig:test-type>checkstyle</sig:test-type>
        <sig:test-description>Checkstyle-Überprüfung mit Omi-Regeln</sig:test-description>
        <sig:test-score>1</sig:test-score>
      </sig:test>
      
      <sig:test id="T02" active="True">
        <sig:test-type>JUnit</sig:test-type
        <sig:test-description>Alle JUnit-Tests ausführen</sig:test-description>
        <sig:test-class>AppTest</sig:test-class>
        <sig:test-score>2</sig:test-score>
      </sig:test>
      
     </sig:tests>
  </sig:task> 
</sig:tasks>
```

The only important subelement is *test-class* because its sets the name of the class file that the Java launcher will run.

As with every test, the test-score value can be any integer.

In the near future it will also be possible to execute just a single test method.

The next step is to add one more test, this time its a text-compare test.

```
<?xml version="1.0" encoding="utf-8"?>
<sig:tasks xmlns:sig="urn:simpelgrader">
 <sig:task id="1000" exercise="EA1" title="Aufgabe EA1">
    <sig:description>description for task 1000</sig:description>
    <sig:files>
      <sig:file>App.java</sig:file>
      <sig:file>AppTest.java</sig:file>
      <sig:file>SchaltjahrTester.java</sig:file>
    </sig:files>
    <sig:actions>
      <sig:action id="A01" active="True" type="java-compile">compile java file</sig:action>
    </sig:actions>
    <sig:tests>
      <sig:test id="T01" active="True">
        <sig:test-type>checkstyle</sig:test-type>
        <sig:test-description>Checkstyle-Überprüfung mit Omi-Regeln</sig:test-description>
        <sig:test-score>1</sig:test-score>
      </sig:test>
      <sig:test id="T02" active="True">
        <sig:test-type>JUnit</sig:test-type
        <sig:test-description>Alle JUnit-Tests ausführen</sig:test-description>
        <sig:test-class>AppTest</sig:test-class>
        <sig:test-score>2</sig:test-score>
      </sig:test>
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<mark><sig:test id="T03" active="True"></mark>
```
        <sig:test-type>TextCompare</sig:test-type>
        <sig:test-description>Ausgabe-Vergleich</sig:test-description>
        <sig:test-testerRegex>(\d+)\s+is\s+a\s+leap year:\s+(\w+)\s+\(expected:\s+(\w+)\)</sig:test-testerRegex>
        <sig:test-testerClass>SchaltjahrTester</sig:test-testerClass>
        <sig:test-score>2</sig:test-score>
      </sig:test>

     </sig:tests>
  </sig:task> 
</sig:tasks>
```

For this kind of test, two subelements are important:

1. test-testerClass
2. test-testerRegex

The test-testClass subelements just contains the name of the class file to be executed by the Java Launcher. Since this is console application, it will output something.

The output consists of several lines. Each line contains the return value from the method implementend in the submitted Java file (eg. App.java) and a expected value.

Here is an example for an output line:

`1 is a leap year: false (expected: false)`

The returned value is false, the expected is also false. Now a regex has to extract these two values:

`(\d+)\s+is\s+a\s+leap year:\s+(\w+)\s+\(expected:\s+(\w+)\)`

It is the task of the author to come up with a Regex that is able to achieve this goal.

I am not using named groups. So the assumption is always that the last group contains the expected value and the second last group the delivered value.

That its for the first exercise EA1. Any other exercise will be included in the grading xml exactly the same way.

A task element in the grading xml does not mean that there have to be submissions for this task in the submission zip file.

It only means that if this task should be graded too, there has to be a definition in the grading xml file.

There is a schema definition file *gradingplan.xsd* - it can be used to validate a grading xml file (my favorite XML editor is <oXygene/> Xml;).

## Setting up the Simpelgrader.ini file

The second major task is setting up at least 9 entries in *Simpelgrader.ini* file.

The following lines all belong in the **[path]** section. Every item name is not case sensitive.

### Step 1: What is the path of the java compiler?

Locate the Java compiler of the Java SDK 11 or higher and put the whole path including java in the javacompilerpath line:

```javacompilerpath = D:\jdk-17\bin\javac```

### Step 2: What is the path of the java launcher?

Locate the Java launcher of the Java SDK 11 or higher and put the whole path including java in the javalauncherpath line:

```javaclauncherpath = D:\jdk-17\bin\java```

### Step 3: What is the path of the jUnit directory?

Locate the path of the JUnit 4.x jar files and put the path in the junitpath line:

```junitpath = D:\Java11\jUnit```

### Step 4: What is the path of the grading plan xml file?

Locate the path of the grading xml file that was setup in the last section of this document and put it in the gradingplanpath line:

``gradingplanpath = G:\2022\Simpelgrader-Testpool\gradingplan3.xml``

### Step 5: What is the path of the submission directory?

Decide in what directory the zip file with the (downloaded) submissions is located and put it in the submissionpath line:

```submissionpath = G:\2022\Simpelgrader-Testpool\submissions```

### Step 6: What is the path of the checkstyle jar file?

Locate the path of the directory with the checkstyle jar file in it and put it in the checkstylepath line:

```checkstylepath = G:\2022\Simpelgrader-Testpool\checkstyle\checkstyle-8.23-all.jar```

### Step 7: What is the path of the checkstyle rule file?

Locate the path of the xml file with the checkstyle rules and put it in the checkstylerulepath line:

```checkstylerulepath = G:\2022\Simpelgrader-Testpool\checkstyle-OMI3d.xml```

### Step 8: What is the path of the csv file with the student names, the roster?

Locate the path of the csv file that contains the student roster and put it in the studentrosterpath line:

```studentrosterpath = G:\2022\Simpelgrader-Testpool\Student_Roster.csv```

### Step 9: What is the path and the name of the Sqlite database file?

Decide in what directory the db file will be located and the name of that file and put the path in the dbpath line:

```dbpath = G:\2022\Simpelgrader-Testpool\simpelv1.db```

The next entries belong to the **[run]** section.

### Step 10: What is the name of semester?

For the report only. Put the name of the semester in the gradesemester line:

```gradesemester = WS 20/21?```

### Step 12: What is the name of module?

For the report only. Put the name of the module in the grademodule line:

```grademodule = GP1```

### Step 13: What is the name of operator?

For the report only. Put the name of the operator in the gradeoperator line:

```gradeoperator = Harcourt Fenton Mud```

The next entries belong to the **[start]** section.

### Step 14: Should the submission directory get deleted before each start?

The default is Yes:

```deletesubmissiontree = Yes```

### Step 15: Should the log file get deleted before each start?

The default is Yes:

```deletelogfile = Yes```

### Step 16: Should the database file backuped before the programm terminates?

The default is No:

```databasebackup = No```

And that's it.

All the settings can be changed in *Simpelgrader* through Menue option I too and of course with any text editor.

## Setting up the submission zip file

*Simpelgrader* expects a single zip file inside the submission directory.

The grading plan consists of a single assignment with three files:

- App.java
- AppTest.java
- Schaltjahrtester.java

If student Fred Meyer uploads his assignment he will upload the file EA1_Fred_Meyer.zip that contains these three files.

When the teacher later downloads the submitted file from Moodle, it will be one zip file that contains each submitted zip file inside another zip file.

So the structure of the downloaded zip file looks like:

```
Moodle_Submission0505_22.zip
--Submission_1_EA1_Fred_Meyer.zip
----EA1_Fred_Meyer.zip
------App.java
------TestApp.java
------Schaltjahrtester.java
```

For testing *Simpelgrader* without Moodle this single zip file has to be packed and has to be inside the submission directory (eg. G:\2022\Simpelgrader-Testpool\submissions)

## First run

Start *Simpelgrader* and choose Menue Option B to extract the zip file into the temp directory (eg. %appdata%\simpelgrader under Windows).

Choose Menue Option D to start the grading run. When its finished, the reports will be shown in the default browser.

That's it.

All the report files are saved in the userprofile directory (eg. %userprofile%\documents\simpelgrader under Windows)

## Browsing the reports

There are several reports.

### the grading action report

This report only contains each grading action and its result.

### the feedback report

This reports contains the feedback (points and message) for each test.

